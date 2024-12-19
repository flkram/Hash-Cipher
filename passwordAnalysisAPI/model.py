import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import random
import time
import os
import multiprocessing
import warnings
from torch.multiprocessing import Pool, set_start_method
import torch.multiprocessing as mp

warnings.filterwarnings("ignore", category=FutureWarning)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

available_cores = multiprocessing.cpu_count()
used_cores = max(1, int(available_cores * 0.8))
torch.set_num_threads(used_cores)

if multiprocessing.current_process().name == "MainProcess":
    print(f"Using device: {DEVICE}")

try:
    set_start_method('spawn')
except RuntimeError:
    pass 

def init_worker(worker_id):
    import sys
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

class PasswordDataset(Dataset):
    def __init__(self, passwords, max_len):
        self.passwords = passwords
        self.max_len = max_len
        self.char_to_idx = {chr(i): i - 31 for i in range(32, 127)}
        self.char_to_idx['<PAD>'] = 0
        self.char_to_idx['<START>'] = len(self.char_to_idx)
        self.char_to_idx['<END>'] = len(self.char_to_idx)
        self.idx_to_char = {i: char for char, i in self.char_to_idx.items()}
        self.vocab_size = len(self.char_to_idx)

    def __len__(self):
        return len(self.passwords)

    def __getitem__(self, idx):
        password = self.passwords[idx]
        encoded = [self.char_to_idx['<START>']]
        for c in password:
            if c in self.char_to_idx:
                encoded.append(self.char_to_idx[c])
        encoded.append(self.char_to_idx['<END>'])
        encoded += [self.char_to_idx['<PAD>']] * (self.max_len - len(encoded))
        return torch.tensor(encoded[:self.max_len], dtype=torch.long)

#Used from https://github.com/gorgarp/TorchPass/blob/main/LICENSE
class PasswordGenerator(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size, num_layers, dropout=0.2):
        super(PasswordGenerator, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.fc = nn.Linear(hidden_size, vocab_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        x = self.layer_norm(x)
        x = self.dropout(x)
        return self.fc(x)

# Train the model
def train_model(model, train_loader, val_loader, loss_fn, optimizer, scheduler, num_epochs, patience=5):
    model.train()
    best_val_loss = float('inf')
    no_improve = 0
    scaler = torch.amp.GradScaler(enabled=torch.cuda.is_available())
    
    for epoch in range(num_epochs):
        start_time = time.time()
        total_train_loss = 0
        
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}"):
            batch = batch.to(DEVICE)
            inputs = batch[:, :-1]
            targets = batch[:, 1:]
            
            optimizer.zero_grad(set_to_none=True)
            
            with torch.amp.autocast(device_type='cuda' if torch.cuda.is_available() else 'cpu'):
                outputs = model(inputs)
                loss = loss_fn(outputs.contiguous().view(-1, outputs.size(-1)), targets.contiguous().view(-1))
            
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
            scaler.step(optimizer)
            scaler.update()
            
            total_train_loss += loss.item()
        
        avg_train_loss = total_train_loss / len(train_loader)
        
        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                batch = batch.to(DEVICE)
                inputs = batch[:, :-1]
                targets = batch[:, 1:]
                
                with torch.amp.autocast(device_type='cuda' if torch.cuda.is_available() else 'cpu'):
                    outputs = model(inputs)
                    loss = loss_fn(outputs.contiguous().view(-1, outputs.size(-1)), targets.contiguous().view(-1))
                total_val_loss += loss.item()
        
        avg_val_loss = total_val_loss / len(val_loader)
        epoch_time = time.time() - start_time
        print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}, Time: {epoch_time:.2f}s")
        
        current_lr = optimizer.param_groups[0]['lr']
        print(f"Current learning rate: {current_lr}")

        scheduler.step(avg_val_loss)
        
        if current_lr != optimizer.param_groups[0]['lr']:
            print(f"Learning rate changed to: {optimizer.param_groups[0]['lr']}")
        
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            no_improve = 0
            torch.save(model.state_dict(), 'best_model.pth')
        else:
            no_improve += 1
            if no_improve >= patience:
                print(f"Early stopping triggered after {epoch+1} epochs")
                break
        
        model.train()
    
    model.load_state_dict(torch.load('best_model.pth', map_location=DEVICE))
    return model

# Generate passwords in a batch
def generate_batch(model, char_to_idx, idx_to_char, batch_size, gpu_id, min_len=8, max_len=26, temp=1.0):
    device = torch.device(f'cuda:{gpu_id}' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    model.eval()
    passwords = [[] for _ in range(batch_size)]
    finished = [False] * batch_size

    with torch.no_grad():
        current_chars = torch.tensor([[char_to_idx['<START>']] for _ in range(batch_size)], dtype=torch.long).to(device)

        for _ in range(max_len):
            outputs = model(current_chars)
            outputs = outputs[:, -1, :] / temp
            probs = torch.softmax(outputs, dim=-1)
            next_chars = torch.multinomial(probs, 1).squeeze(1)

            for i, next_char in enumerate(next_chars):
                if next_char == char_to_idx['<END>'] and len(passwords[i]) >= min_len:
                    finished[i] = True
                elif next_char != char_to_idx['<PAD>'] and not finished[i]:
                    passwords[i].append(idx_to_char[next_char.item()])

            if all(finished):
                break

            current_chars = torch.cat([current_chars, next_chars.unsqueeze(1)], dim=1)

    return [''.join(pwd) for pwd in passwords if len(pwd) >= min_len]

# Generate passwords with multiprocessing
def generate_passwords(model, char_to_idx, idx_to_char, num_passwords, batch_size, num_workers, temp):
    total_generated = 0
    passwords = []
    num_gpus = torch.cuda.device_count()

    model = model.cpu()

    with mp.Pool(processes=num_workers) as pool:
        pbar = tqdm(total=num_passwords, desc="Generating passwords")
        
        while total_generated < num_passwords:
            batch_results = [pool.apply_async(generate_batch, (model, char_to_idx, idx_to_char, batch_size, i % max(num_gpus, 1),  temp)) for i in range(num_workers)]
            for result in batch_results:
                batch_passwords = result.get()
                passwords.extend(batch_passwords)
                new_passwords = len(batch_passwords)
                total_generated += new_passwords
                pbar.update(new_passwords)
        
        pbar.close()

    return passwords[:num_passwords]

def runner(
    mode: str,
    input_file: str = 'input.txt',
    output_file: str = 'output.txt',
    model_path: str = 'model.pth',
    epochs: int = 50,
    batch_size: int = 256,
    num_passwords: int = 100,
    temperature: float = 1.0,
    num_workers: int = 4
):
    if mode == 'train':
        if not input_file:
            raise ValueError("Input file required for training")
        
        if os.path.exists(model_path):
            os.remove(model_path)
            
        print("Initializing a new model.")
        char_to_idx = {chr(i): i - 31 for i in range(32, 127)}
        char_to_idx['<PAD>'] = 0
        char_to_idx['<START>'] = len(char_to_idx)
        char_to_idx['<END>'] = len(char_to_idx)
        idx_to_char = {i: char for char, i in char_to_idx.items()}
        model = PasswordGenerator(len(char_to_idx), embed_size=256, hidden_size=512, num_layers=3)
        model.to(DEVICE)

        with open(input_file, 'r', encoding='latin-1') as f:
            passwords = [line.strip() for line in f if 8 <= len(line.strip()) <= 26 and all(32 <= ord(c) < 127 for c in line.strip())]

        random.shuffle(passwords)
        max_len = 28
        train_passwords = passwords[:int(0.9 * len(passwords))]
        val_passwords = passwords[int(0.9 * len(passwords)):]

        train_dataset = PasswordDataset(train_passwords, max_len)
        val_dataset = PasswordDataset(val_passwords, max_len)

        train_dataset.char_to_idx = char_to_idx
        train_dataset.idx_to_char = idx_to_char
        train_dataset.vocab_size = len(char_to_idx)
        val_dataset.char_to_idx = char_to_idx
        val_dataset.idx_to_char = idx_to_char
        val_dataset.vocab_size = len(char_to_idx)

        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True,
            persistent_workers=True
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
            persistent_workers=True
        )

        print("Starting training...")
        loss_fn = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters())
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)
        model = train_model(model, train_loader, val_loader, loss_fn, optimizer, scheduler, epochs)

        torch.save({
            'model_state_dict': model.state_dict(),
            'char_to_idx': char_to_idx,
            'idx_to_char': idx_to_char
        }, model_path)
        print(f"Model saved: {model_path}")

    elif mode == 'generate':
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not output_file:
            raise ValueError("Output file required for generation")

        print(f"Loading model: {model_path}")
        checkpoint = torch.load(model_path, map_location='cpu')
        char_to_idx = checkpoint['char_to_idx']
        idx_to_char = checkpoint['idx_to_char']
        model = PasswordGenerator(len(char_to_idx), embed_size=256, hidden_size=512, num_layers=3)
        model.load_state_dict(checkpoint['model_state_dict'])

        model.eval()

        print(f"Generating passwords...")
        passwords = generate_passwords(model, char_to_idx, idx_to_char, num_passwords, batch_size, num_workers, temperature)

        with open(output_file, 'w', encoding='utf-8') as f:
            for password in passwords:
                f.write(f"{password}\n")

        print(f"Passwords saved to: {output_file}")
        
def searcher(password: str, input_file: str = 'input.txt') -> int:
    """
    Counts the number of lines in the input file that are substrings of the given password.
    """
    count = 0
    with open(input_file, 'r', encoding='latin-1') as file:
        for line in file:
            line = line.strip()
            if line in password:
                count += 1
    return count

def newPassword(input_file: str = 'output.txt') -> str:
    """
    Randomly selects a line from the first 1000 lines of the input file.

    """
    
    lines = []
    with open(input_file, 'r', encoding='latin-1') as file:
        for idx, line in enumerate(file):
            if idx >= 100:
                break
            lines.append(line.strip())
    return random.choice(lines) if lines else ""

    # lineNum = random.randint(1000)
    # with open(input_file, 'r', encoding='latin-1') as file:
    #     res = file.readline()
    #     for i in range(lineNum):
    #         res = file.readline()
    #     res
    
def resetInput():
    # os.remove('input.txt')
    # with open('input.txt', 'w') as newFile:
    #     newFile.writelines(["password\r", "default\r", "pass123"])
    addInput(["password", "password2"])

def addInput(newLines):
    with open('input.txt', 'a') as inputFile:
        for line in newLines:
            inputFile.write(line+'\n')
            
        


