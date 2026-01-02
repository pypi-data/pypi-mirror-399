import torch
import torch.nn as nn
import torch.optim as optim
import time
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from tether.nn import LIF
from tether.data import SpikingDatasetWrapper, rate_encoding
from tether.utils.monitor import Monitor  #


class SpikingCIFARModel(nn.Module):
    def __init__(self, n_steps=10):
        super().__init__()
        self.n_steps = n_steps

        # Define layers
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            LIF(32 * 32 * 32),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            LIF(64 * 16 * 16),
            nn.MaxPool2d(2),
        )

        self.fc_layers = nn.Sequential(
            nn.Flatten(), nn.Linear(64 * 8 * 8, 256), LIF(256), nn.Linear(256, 10)
        )

    def forward(self, x):
        # x shape: (Time, Batch, C, H, W)
        outputs = []
        for t in range(self.n_steps):
            x_t = x[t]
            feat = self.conv_layers(x_t)
            out = self.fc_layers(feat)
            outputs.append(out)
        return torch.stack(outputs).mean(0)


def evaluate(model, loader, device):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for data, target in loader:
            data = data.to(device).transpose(0, 1)
            target = target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += (pred == target).sum().item()
            total += target.size(0)
    return 100.0 * correct / total


def main():
    # --- Configuration ---
    device = "cuda" if torch.cuda.is_available() else "cpu"
    n_steps = 10
    batch_size = 64
    epochs = 10
    lr = 1e-3

    # --- Data Preparation ---
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )

    train_raw = datasets.CIFAR10(
        root="./data", train=True, download=True, transform=transform
    )
    test_raw = datasets.CIFAR10(
        root="./data", train=False, download=True, transform=transform
    )

    train_ds = SpikingDatasetWrapper(
        train_raw, encode_fn=lambda x: rate_encoding(x, n_steps=n_steps)
    )
    test_ds = SpikingDatasetWrapper(
        test_raw, encode_fn=lambda x: rate_encoding(x, n_steps=n_steps)
    )

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=4
    )
    test_loader = DataLoader(
        test_ds, batch_size=batch_size, shuffle=False, num_workers=4
    )

    # --- Model & Monitoring ---
    model = SpikingCIFARModel(n_steps=n_steps).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    # Initialize the Tether Monitor
    monitor = Monitor(model)

    print(f"Starting Tether CIFAR-10 Training on {device}")
    print("-" * 60)

    # --- Training Loop ---
    for epoch in range(epochs):
        model.train()
        start_time = time.time()
        running_loss = 0.0
        train_correct = 0
        train_total = 0

        for data, target in train_loader:
            data = data.to(device).transpose(0, 1)
            target = target.to(device)

            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            # Track training metrics
            running_loss += loss.item()
            pred = output.argmax(dim=1)
            train_correct += (pred == target).sum().item()
            train_total += target.size(0)

        # --- End of Epoch Monitoring ---
        epoch_time = time.time() - start_time
        avg_loss = running_loss / len(train_loader)
        train_acc = 100.0 * train_correct / train_total
        val_acc = evaluate(model, test_loader, device)

        # Retrieve firing rates from all LIF layers via Monitor
        firing_rates = monitor.get_firing_rates()
        # Calculate mean firing rate across the entire model
        mean_fr = (
            sum(firing_rates.values()) / len(firing_rates) if firing_rates else 0.0
        )

        # Print detailed report once per epoch
        print(f"Epoch {epoch + 1}/{epochs} | Time: {epoch_time:.1f}s")
        print(
            f"  > Loss: {avg_loss:.4f} | Train Acc: {train_acc:.2f}% | Val Acc: {val_acc:.2f}%"
        )
        print(
            f"  > Mean Firing Rate: {mean_fr:.4f} (Sparsity: {(1 - mean_fr) * 100:.1f}%)"
        )
        print("-" * 60)


if __name__ == "__main__":
    main()
