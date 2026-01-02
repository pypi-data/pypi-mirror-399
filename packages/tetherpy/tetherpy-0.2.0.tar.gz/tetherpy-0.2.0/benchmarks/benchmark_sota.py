"""
Comprehensive Benchmark Suite for Tether vs snnTorch vs SpikingJelly

Usage:
    python benchmarks/compare_frameworks.py --task all --save-results
    python benchmarks/compare_frameworks.py --task cifar10 --frameworks tether snntorch
    python benchmarks/compare_frameworks.py --task mnist --epochs 10
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from dataclasses import dataclass, asdict
import psutil
import GPUtil

# Framework imports with error handling
FRAMEWORKS_AVAILABLE = {}

try:
    from tether.nn import LIF as TetherLIF
    from tether.data import SpikingDatasetWrapper, rate_encoding
    FRAMEWORKS_AVAILABLE['tether'] = True
except ImportError:
    FRAMEWORKS_AVAILABLE['tether'] = False
    print("WARNING: Tether not available")

try:
    import snntorch as snn
    from snntorch import surrogate
    FRAMEWORKS_AVAILABLE['snntorch'] = True
except ImportError:
    FRAMEWORKS_AVAILABLE['snntorch'] = False
    print("WARNING: snnTorch not available")

try:
    from spikingjelly.activation_based import neuron, functional, layer
    FRAMEWORKS_AVAILABLE['spikingjelly'] = True
except ImportError:
    FRAMEWORKS_AVAILABLE['spikingjelly'] = False
    print("WARNING: SpikingJelly not available")


@dataclass
class BenchmarkResult:
    """Store benchmark results for a single run."""
    framework: str
    task: str
    model: str
    epochs: int
    batch_size: int
    n_steps: int
    
    # Performance metrics
    final_train_acc: float
    final_test_acc: float
    best_test_acc: float
    total_time_seconds: float
    avg_epoch_time: float
    avg_step_time: float
    
    # Resource metrics
    peak_memory_mb: float
    avg_gpu_util: float
    
    # Training dynamics
    train_accs: List[float]
    test_accs: List[float]
    epoch_times: List[float]
    
    # Hardware info
    gpu_name: str
    cuda_version: str
    
    def speedup_vs(self, baseline: 'BenchmarkResult') -> float:
        """Calculate speedup relative to baseline."""
        return baseline.total_time_seconds / self.total_time_seconds
    
    def to_dict(self):
        return asdict(self)


class GPUMonitor:
    """Monitor GPU utilization and memory."""
    def __init__(self):
        self.gpu_utils = []
        self.memory_uses = []
        
    def sample(self):
        """Take a sample of current GPU state."""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                self.gpu_utils.append(gpu.load * 100)
                self.memory_uses.append(gpu.memoryUsed)
        except:
            pass
    
    def get_stats(self) -> Tuple[float, float]:
        """Return (avg_util, peak_memory)."""
        avg_util = np.mean(self.gpu_utils) if self.gpu_utils else 0.0
        peak_mem = max(self.memory_uses) if self.memory_uses else 0.0
        return avg_util, peak_mem


# ============================================================================
# MODEL DEFINITIONS
# ============================================================================

class TetherCIFAR10Model(nn.Module):
    """Tether model for CIFAR-10."""
    def __init__(self, n_steps=10):
        super().__init__()
        self.n_steps = n_steps
        
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1),
            TetherLIF(64 * 32 * 32),
            nn.AvgPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            TetherLIF(128 * 16 * 16),
            nn.AvgPool2d(2),
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 8 * 8, 256),
            TetherLIF(256),
            nn.Linear(256, 10)
        )
    
    def forward(self, x):
        # x: (Batch, Time, C, H, W) or (Time, Batch, C, H, W)
        if len(x.shape) == 5 and x.shape[0] != self.n_steps:
            x = x.transpose(0, 1)  # (Time, Batch, C, H, W)
        
        outputs = []
        for t in range(self.n_steps):
            x_t = x[t]
            feat = self.features(x_t)
            out = self.classifier(feat)
            outputs.append(out)
        
        return torch.stack(outputs).mean(0)


class TetherMNISTModel(nn.Module):
    """Tether model for MNIST."""
    def __init__(self, n_steps=10):
        super().__init__()
        self.n_steps = n_steps
        
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            TetherLIF(32 * 28 * 28),
            nn.AvgPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            TetherLIF(64 * 14 * 14),
            nn.AvgPool2d(2),
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),
            TetherLIF(128),
            nn.Linear(128, 10)
        )
    
    def forward(self, x):
        if len(x.shape) == 5 and x.shape[0] != self.n_steps:
            x = x.transpose(0, 1)
        
        outputs = []
        for t in range(self.n_steps):
            x_t = x[t]
            feat = self.features(x_t)
            out = self.classifier(feat)
            outputs.append(out)
        
        return torch.stack(outputs).mean(0)


class SNNTorchCIFAR10Model(nn.Module):
    """snnTorch model for CIFAR-10."""
    def __init__(self, n_steps=10, beta=0.9):
        super().__init__()
        self.n_steps = n_steps
        
        spike_grad = surrogate.fast_sigmoid()
        
        self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
        self.lif1 = snn.Leaky(beta=beta, spike_grad=spike_grad, init_hidden=True)
        self.pool1 = nn.AvgPool2d(2)
        
        self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
        self.lif2 = snn.Leaky(beta=beta, spike_grad=spike_grad, init_hidden=True)
        self.pool2 = nn.AvgPool2d(2)
        
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(128 * 8 * 8, 256)
        self.lif3 = snn.Leaky(beta=beta, spike_grad=spike_grad, init_hidden=True)
        self.fc2 = nn.Linear(256, 10)
    
    def forward(self, x):
        # Reset hidden states
        self.lif1.init_leaky()
        self.lif2.init_leaky()
        self.lif3.init_leaky()
        
        outputs = []
        for t in range(self.n_steps):
            x_t = x[:, t] if x.shape[1] == self.n_steps else x[t]
            
            cur = self.conv1(x_t)
            spk = self.lif1(cur)
            cur = self.pool1(spk)
            
            cur = self.conv2(cur)
            spk = self.lif2(cur)
            cur = self.pool2(spk)
            
            cur = self.flatten(cur)
            cur = self.fc1(cur)
            spk = self.lif3(cur)
            cur = self.fc2(spk)
            
            outputs.append(cur)
        
        return torch.stack(outputs).mean(0)


class SNNTorchMNISTModel(nn.Module):
    """snnTorch model for MNIST."""
    def __init__(self, n_steps=10, beta=0.9):
        super().__init__()
        self.n_steps = n_steps
        
        spike_grad = surrogate.fast_sigmoid()
        
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
        self.lif1 = snn.Leaky(beta=beta, spike_grad=spike_grad, init_hidden=True)
        self.pool1 = nn.AvgPool2d(2)
        
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.lif2 = snn.Leaky(beta=beta, spike_grad=spike_grad, init_hidden=True)
        self.pool2 = nn.AvgPool2d(2)
        
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.lif3 = snn.Leaky(beta=beta, spike_grad=spike_grad, init_hidden=True)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        # Reset hidden states
        self.lif1.init_leaky()
        self.lif2.init_leaky()
        self.lif3.init_leaky()
        
        outputs = []
        for t in range(self.n_steps):
            x_t = x[:, t] if x.shape[1] == self.n_steps else x[t]
            
            cur = self.conv1(x_t)
            spk = self.lif1(cur)
            cur = self.pool1(spk)
            
            cur = self.conv2(cur)
            spk = self.lif2(cur)
            cur = self.pool2(spk)
            
            cur = self.flatten(cur)
            cur = self.fc1(cur)
            spk = self.lif3(cur)
            cur = self.fc2(spk)
            
            outputs.append(cur)
        
        return torch.stack(outputs).mean(0)


class SpikingJellyCIFAR10Model(nn.Module):
    """SpikingJelly model for CIFAR-10."""
    def __init__(self, n_steps=10):
        super().__init__()
        self.n_steps = n_steps
        
        self.features = nn.Sequential(
            layer.Conv2d(3, 64, 3, padding=1),
            neuron.IFNode(surrogate_function=neuron.surrogate.ATan()),
            layer.AvgPool2d(2),
            layer.Conv2d(64, 128, 3, padding=1),
            neuron.IFNode(surrogate_function=neuron.surrogate.ATan()),
            layer.AvgPool2d(2),
        )
        
        self.classifier = nn.Sequential(
            layer.Flatten(),
            layer.Linear(128 * 8 * 8, 256),
            neuron.IFNode(surrogate_function=neuron.surrogate.ATan()),
            layer.Linear(256, 10)
        )
    
    def forward(self, x):
        # x: (Batch, Time, C, H, W)
        # SpikingJelly expects (Time, Batch, C, H, W)
        if len(x.shape) == 5:
            if x.shape[1] == self.n_steps:
                x = x.transpose(0, 1)
        
        outputs = []
        functional.reset_net(self)
        
        for t in range(self.n_steps):
            x_t = x[t]
            feat = self.features(x_t)
            out = self.classifier(feat)
            outputs.append(out)
        
        return torch.stack(outputs).mean(0)


class SpikingJellyMNISTModel(nn.Module):
    """SpikingJelly model for MNIST."""
    def __init__(self, n_steps=10):
        super().__init__()
        self.n_steps = n_steps
        
        self.features = nn.Sequential(
            layer.Conv2d(1, 32, 3, padding=1),
            neuron.IFNode(surrogate_function=neuron.surrogate.ATan()),
            layer.AvgPool2d(2),
            layer.Conv2d(32, 64, 3, padding=1),
            neuron.IFNode(surrogate_function=neuron.surrogate.ATan()),
            layer.AvgPool2d(2),
        )
        
        self.classifier = nn.Sequential(
            layer.Flatten(),
            layer.Linear(64 * 7 * 7, 128),
            neuron.IFNode(surrogate_function=neuron.surrogate.ATan()),
            layer.Linear(128, 10)
        )
    
    def forward(self, x):
        if len(x.shape) == 5:
            if x.shape[1] == self.n_steps:
                x = x.transpose(0, 1)
        
        outputs = []
        functional.reset_net(self)
        
        for t in range(self.n_steps):
            x_t = x[t]
            feat = self.features(x_t)
            out = self.classifier(feat)
            outputs.append(out)
        
        return torch.stack(outputs).mean(0)


# ============================================================================
# DATA LOADING
# ============================================================================

def get_mnist_loaders(batch_size=64, n_steps=10, framework='tether'):
    """Get MNIST data loaders."""
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    data_root = './data'
    Path(data_root).mkdir(exist_ok=True, parents=True)
    
    print(f"Loading MNIST dataset (will download if not present in {data_root})...")
    
    try:
        train_dataset = torchvision.datasets.MNIST(
            root=data_root, train=True, download=True, transform=transform
        )
        test_dataset = torchvision.datasets.MNIST(
            root=data_root, train=False, download=True, transform=transform
        )
    except Exception as e:
        print(f"ERROR: Failed to download MNIST: {e}")
        print("Please check your internet connection or download manually from:")
        print("http://yann.lecun.com/exdb/mnist/")
        raise
    
    if framework == 'tether':
        from tether.data import SpikingDatasetWrapper, rate_encoding
        train_dataset = SpikingDatasetWrapper(
            train_dataset, 
            encode_fn=lambda x: rate_encoding(x, n_steps=n_steps)
        )
        test_dataset = SpikingDatasetWrapper(
            test_dataset,
            encode_fn=lambda x: rate_encoding(x, n_steps=n_steps)
        )
    elif framework in ['snntorch', 'spikingjelly']:
        # These frameworks handle encoding internally or expect different format
        # We'll replicate the data across time dimension
        class TimeReplicateDataset(torch.utils.data.Dataset):
            def __init__(self, base_dataset, n_steps):
                self.base = base_dataset
                self.n_steps = n_steps
            
            def __len__(self):
                return len(self.base)
            
            def __getitem__(self, idx):
                x, y = self.base[idx]
                # Replicate across time: (C, H, W) -> (T, C, H, W)
                x_time = x.unsqueeze(0).repeat(self.n_steps, 1, 1, 1)
                return x_time, y
        
        train_dataset = TimeReplicateDataset(train_dataset, n_steps)
        test_dataset = TimeReplicateDataset(test_dataset, n_steps)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    
    return train_loader, test_loader


def get_cifar10_loaders(batch_size=64, n_steps=10, framework='tether'):
    """Get CIFAR-10 data loaders."""
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    data_root = './data'
    Path(data_root).mkdir(exist_ok=True, parents=True)
    
    print(f"Loading CIFAR-10 dataset (will download if not present in {data_root})...")
    
    try:
        train_dataset = torchvision.datasets.CIFAR10(
            root=data_root, train=True, download=True, transform=transform
        )
        test_dataset = torchvision.datasets.CIFAR10(
            root=data_root, train=False, download=True, transform=transform
        )
    except Exception as e:
        print(f"ERROR: Failed to download CIFAR-10: {e}")
        print("Please check your internet connection or download manually from:")
        print("https://www.cs.toronto.edu/~kriz/cifar.html")
        raise
    
    if framework == 'tether':
        from tether.data import SpikingDatasetWrapper, rate_encoding
        train_dataset = SpikingDatasetWrapper(
            train_dataset,
            encode_fn=lambda x: rate_encoding(x, n_steps=n_steps)
        )
        test_dataset = SpikingDatasetWrapper(
            test_dataset,
            encode_fn=lambda x: rate_encoding(x, n_steps=n_steps)
        )
    elif framework in ['snntorch', 'spikingjelly']:
        class TimeReplicateDataset(torch.utils.data.Dataset):
            def __init__(self, base_dataset, n_steps):
                self.base = base_dataset
                self.n_steps = n_steps
            
            def __len__(self):
                return len(self.base)
            
            def __getitem__(self, idx):
                x, y = self.base[idx]
                x_time = x.unsqueeze(0).repeat(self.n_steps, 1, 1, 1)
                return x_time, y
        
        train_dataset = TimeReplicateDataset(train_dataset, n_steps)
        test_dataset = TimeReplicateDataset(test_dataset, n_steps)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    
    return train_loader, test_loader


# ============================================================================
# TRAINING & EVALUATION
# ============================================================================

def train_epoch(model, loader, optimizer, criterion, device, gpu_monitor):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    for batch_idx, (data, target) in enumerate(loader):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        pred = output.argmax(dim=1)
        correct += pred.eq(target).sum().item()
        total += target.size(0)
        
        if batch_idx % 10 == 0:
            gpu_monitor.sample()
    
    return total_loss / len(loader), 100. * correct / total


def evaluate(model, loader, device):
    """Evaluate model."""
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.size(0)
    
    return 100. * correct / total


def benchmark_framework(
    framework: str,
    task: str,
    epochs: int = 10,
    batch_size: int = 64,
    n_steps: int = 10,
    device: str = 'cuda'
) -> BenchmarkResult:
    """Run benchmark for a specific framework and task."""
    
    print(f"\n{'='*60}")
    print(f"Benchmarking {framework.upper()} on {task.upper()}")
    print(f"{'='*60}")
    
    # Get model
    if task == 'mnist':
        if framework == 'tether':
            model = TetherMNISTModel(n_steps=n_steps)
        elif framework == 'snntorch':
            model = SNNTorchMNISTModel(n_steps=n_steps)
        elif framework == 'spikingjelly':
            model = SpikingJellyMNISTModel(n_steps=n_steps)
        train_loader, test_loader = get_mnist_loaders(batch_size, n_steps, framework)
    
    elif task == 'cifar10':
        if framework == 'tether':
            model = TetherCIFAR10Model(n_steps=n_steps)
        elif framework == 'snntorch':
            model = SNNTorchCIFAR10Model(n_steps=n_steps)
        elif framework == 'spikingjelly':
            model = SpikingJellyCIFAR10Model(n_steps=n_steps)
        train_loader, test_loader = get_cifar10_loaders(batch_size, n_steps, framework)
    
    else:
        raise ValueError(f"Unknown task: {task}")
    
    model = model.to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()
    
    # Initialize monitoring
    gpu_monitor = GPUMonitor()
    
    # Training loop
    train_accs = []
    test_accs = []
    epoch_times = []
    
    total_start = time.time()
    
    for epoch in range(epochs):
        epoch_start = time.time()
        
        train_loss, train_acc = train_epoch(
            model, train_loader, optimizer, criterion, device, gpu_monitor
        )
        test_acc = evaluate(model, test_loader, device)
        
        epoch_time = time.time() - epoch_start
        
        train_accs.append(train_acc)
        test_accs.append(test_acc)
        epoch_times.append(epoch_time)
        
        print(f"Epoch {epoch+1}/{epochs} | "
              f"Train Acc: {train_acc:.2f}% | "
              f"Test Acc: {test_acc:.2f}% | "
              f"Time: {epoch_time:.2f}s")
    
    total_time = time.time() - total_start
    
    # Get GPU stats
    avg_gpu_util, peak_memory = gpu_monitor.get_stats()
    
    # Get hardware info
    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    cuda_version = torch.version.cuda if torch.cuda.is_available() else "N/A"
    
    result = BenchmarkResult(
        framework=framework,
        task=task,
        model=model.__class__.__name__,
        epochs=epochs,
        batch_size=batch_size,
        n_steps=n_steps,
        final_train_acc=train_accs[-1],
        final_test_acc=test_accs[-1],
        best_test_acc=max(test_accs),
        total_time_seconds=total_time,
        avg_epoch_time=np.mean(epoch_times),
        avg_step_time=total_time / (epochs * len(train_loader)),
        peak_memory_mb=peak_memory,
        avg_gpu_util=avg_gpu_util,
        train_accs=train_accs,
        test_accs=test_accs,
        epoch_times=epoch_times,
        gpu_name=gpu_name,
        cuda_version=cuda_version
    )
    
    return result


# ============================================================================
# RESULTS ANALYSIS & REPORTING
# ============================================================================

def compare_results(results: List[BenchmarkResult]) -> Dict:
    """Compare results across frameworks."""
    if not results:
        return {}
    
    # Group by task
    by_task = {}
    for r in results:
        if r.task not in by_task:
            by_task[r.task] = []
        by_task[r.task].append(r)
    
    comparison = {}
    
    for task, task_results in by_task.items():
        # Find baseline (slowest)
        baseline = max(task_results, key=lambda x: x.total_time_seconds)
        
        task_comparison = {
            'baseline': baseline.framework,
            'frameworks': {}
        }
        
        for r in task_results:
            speedup = baseline.total_time_seconds / r.total_time_seconds
            
            task_comparison['frameworks'][r.framework] = {
                'time': r.total_time_seconds,
                'speedup': f"{speedup:.2f}x",
                'accuracy': r.best_test_acc,
                'memory_mb': r.peak_memory_mb,
                'gpu_util': r.avg_gpu_util
            }
        
        comparison[task] = task_comparison
    
    return comparison


def generate_markdown_report(results: List[BenchmarkResult], output_path: str):
    """Generate a markdown report."""
    
    comparison = compare_results(results)
    
    report = f"""# SNN Framework Benchmark Results

**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}
**Hardware:** {results[0].gpu_name if results else 'N/A'}
**CUDA Version:** {results[0].cuda_version if results else 'N/A'}

## Summary

"""
    
    for task, comp in comparison.items():
        report += f"\n### {task.upper()}\n\n"
        report += "| Framework | Time | Speedup | Best Acc | Memory (MB) | GPU Util |\n"
        report += "|-----------|------|---------|----------|-------------|----------|\n"
        
        for fw, stats in comp['frameworks'].items():
            report += f"| {fw} | {stats['time']:.1f}s | {stats['speedup']} | "
            report += f"{stats['accuracy']:.2f}% | {stats['memory_mb']:.1f} | "
            report += f"{stats['gpu_util']:.1f}% |\n"
    
    report += "\n## Detailed Results\n\n"
    
    for result in results:
        report += f"\n### {result.framework.upper()} - {result.task.upper()}\n\n"
        report += f"- **Total Time:** {result.total_time_seconds:.2f}s\n"
        report += f"- **Avg Epoch Time:** {result.avg_epoch_time:.2f}s\n"
        report += f"- **Final Test Accuracy:** {result.final_test_acc:.2f}%\n"
        report += f"- **Best Test Accuracy:** {result.best_test_acc:.2f}%\n"
        report += f"- **Peak Memory:** {result.peak_memory_mb:.1f} MB\n"
        report += f"- **Avg GPU Utilization:** {result.avg_gpu_util:.1f}%\n\n"
        
        report += "**Training Progress:**\n\n"
        for i, (train_acc, test_acc, epoch_time) in enumerate(
            zip(result.train_accs, result.test_accs, result.epoch_times), 1
        ):
            report += f"- Epoch {i}: Train {train_acc:.2f}%, Test {test_acc:.2f}%, Time {epoch_time:.2f}s\n"
    
    report += "\n## Methodology\n\n"
    report += f"- **Batch Size:** {results[0].batch_size}\n"
    report += f"- **Time Steps:** {results[0].n_steps}\n"
    report += f"- **Epochs:** {results[0].epochs}\n"
    report += "- **Optimizer:** Adam (lr=1e-3)\n"
    report += "- **Loss:** CrossEntropyLoss\n"
    report += "\nAll experiments run with identical hyperparameters and network architectures "
    report += "(accounting for framework-specific API differences).\n"
    
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to {output_path}")


def save_results_json(results: List[BenchmarkResult], output_path: str):
    """Save results as JSON."""
    data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'results': [r.to_dict() for r in results]
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Results saved to {output_path}")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Benchmark SNN Frameworks')
    parser.add_argument('--task', type=str, default='all', 
                       choices=['mnist', 'cifar10', 'all'],
                       help='Task to benchmark')
    parser.add_argument('--frameworks', nargs='+', 
                       default=['tether', 'snntorch', 'spikingjelly'],
                       help='Frameworks to benchmark')
    parser.add_argument('--epochs', type=int, default=10,
                       help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=64,
                       help='Batch size')
    parser.add_argument('--n-steps', type=int, default=10,
                       help='Number of time steps')
    parser.add_argument('--save-results', action='store_true',
                       help='Save results to files')
    parser.add_argument('--output-dir', type=str, default='./benchmark_results',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    # Setup
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if device == 'cpu':
        print("WARNING: CUDA not available. Benchmarks will be slow and less meaningful.")
    
    # Determine tasks
    tasks = ['mnist', 'cifar10'] if args.task == 'all' else [args.task]
    
    # Filter available frameworks
    frameworks_to_test = [
        fw for fw in args.frameworks 
        if FRAMEWORKS_AVAILABLE.get(fw, False)
    ]
    
    if not frameworks_to_test:
        print("ERROR: No frameworks available for testing!")
        print("Install at least one of: tether, snntorch, spikingjelly")
        return
    
    print(f"\nStarting Benchmark")
    print(f"Tasks: {tasks}")
    print(f"Frameworks: {frameworks_to_test}")
    print(f"Device: {device}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Time Steps: {args.n_steps}\n")
    
    # Run benchmarks
    results = []
    
    for task in tasks:
        for framework in frameworks_to_test:
            try:
                result = benchmark_framework(
                    framework=framework,
                    task=task,
                    epochs=args.epochs,
                    batch_size=args.batch_size,
                    n_steps=args.n_steps,
                    device=device
                )
                results.append(result)
            except Exception as e:
                print(f"ERROR: Error benchmarking {framework} on {task}: {e}")
                import traceback
                traceback.print_exc()
    
    if not results:
        print("ERROR: No successful benchmark runs!")
        return
    
    # Print summary
    print("\n" + "="*60)
    print("BENCHMARK COMPLETE")
    print("="*60)
    
    comparison = compare_results(results)
    for task, comp in comparison.items():
        print(f"\n{task.upper()} Results:")
        print(f"Baseline: {comp['baseline']}")
        for fw, stats in comp['frameworks'].items():
            print(f"  {fw:15s}: {stats['speedup']:>6s} | Acc: {stats['accuracy']:>6.2f}% | Time: {stats['time']:>6.1f}s")
    
    # Save results
    if args.save_results:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        json_path = output_dir / f"results_{timestamp}.json"
        md_path = output_dir / f"report_{timestamp}.md"
        
        save_results_json(results, str(json_path))
        generate_markdown_report(results, str(md_path))
        
        print(f"\nResults saved to {output_dir}")


if __name__ == '__main__':
    main()