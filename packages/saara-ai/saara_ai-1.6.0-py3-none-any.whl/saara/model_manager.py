"""
Model Manager Module
Handles Ollama model installation, management, and hardware-based recommendations.
"""

import logging
import subprocess
import json
import psutil
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

import requests

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class ModelInfo:
    """Information about an Ollama model."""
    name: str
    display_name: str
    category: str  # vision, analyzer, embedding
    size_gb: float
    vram_required: float  # GB
    description: str
    tags: List[str] = field(default_factory=list)
    is_installed: bool = False


# Model catalog organized by category and hardware requirements
MODEL_CATALOG = {
    "vision": [
        # Lightweight (< 4GB VRAM)
        ModelInfo("moondream", "Moondream 2", "vision", 1.5, 2.0, 
                  "Fast, lightweight vision model. Best for quick OCR.", ["lightweight", "fast"]),
        ModelInfo("llava:7b", "LLaVA 7B", "vision", 4.0, 4.5,
                  "Good balance of speed and accuracy.", ["balanced"]),
        # Medium (4-8GB VRAM)
        ModelInfo("qwen2.5vl:3b", "Qwen2.5-VL 3B", "vision", 2.0, 3.5,
                  "Alibaba's vision model. Good for tables.", ["tables", "chinese"]),
        ModelInfo("qwen2.5vl:7b", "Qwen2.5-VL 7B", "vision", 4.5, 6.0,
                  "Higher accuracy vision model.", ["accurate"]),
        # Heavy (> 8GB VRAM)
        ModelInfo("llava:13b", "LLaVA 13B", "vision", 8.0, 10.0,
                  "High accuracy, slower. For detailed documents.", ["accurate", "slow"]),
        ModelInfo("qwen2.5vl:32b", "Qwen2.5-VL 32B", "vision", 20.0, 24.0,
                  "Best accuracy. Requires high-end GPU.", ["best", "heavy"]),
    ],
    "analyzer": [
        # Lightweight (< 4GB VRAM)
        ModelInfo("phi3:mini", "Phi-3 Mini", "analyzer", 2.0, 2.5,
                  "Microsoft's compact model. Fast inference.", ["lightweight", "fast"]),
        ModelInfo("gemma2:2b", "Gemma 2 2B", "analyzer", 1.5, 2.0,
                  "Google's small model. Good for simple tasks.", ["lightweight"]),
        ModelInfo("qwen2.5:3b", "Qwen 2.5 3B", "analyzer", 2.0, 3.0,
                  "Alibaba's efficient small model.", ["lightweight", "multilingual"]),
        # Medium (4-8GB VRAM)
        ModelInfo("llama3.2:3b", "Llama 3.2 3B", "analyzer", 2.0, 3.5,
                  "Meta's latest efficient model.", ["balanced"]),
        ModelInfo("granite3.1-dense:8b", "Granite 3.1 8B", "analyzer", 4.5, 6.0,
                  "IBM's enterprise model. Great for data tasks.", ["enterprise", "structured"]),
        ModelInfo("mistral:7b", "Mistral 7B", "analyzer", 4.0, 5.5,
                  "Fast and capable. Good general model.", ["balanced", "fast"]),
        ModelInfo("qwen2.5:7b", "Qwen 2.5 7B", "analyzer", 4.5, 6.0,
                  "Excellent reasoning and multilingual.", ["reasoning", "multilingual"]),
        # Heavy (> 8GB VRAM)
        ModelInfo("llama3.2:70b", "Llama 3.2 70B", "analyzer", 40.0, 48.0,
                  "Most powerful open model. Requires multiple GPUs.", ["best", "heavy"]),
        ModelInfo("qwen2.5:32b", "Qwen 2.5 32B", "analyzer", 20.0, 24.0,
                  "Excellent for complex reasoning.", ["reasoning", "heavy"]),
        ModelInfo("deepseek-coder-v2:16b", "DeepSeek Coder V2 16B", "analyzer", 10.0, 12.0,
                  "Best for code and structured data.", ["code", "technical"]),
    ],
}


class HardwareDetector:
    """Detects system hardware capabilities."""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get detailed system information."""
        info = {
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 1),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "gpu_available": False,
            "gpu_name": None,
            "vram_gb": 0,
        }
        
        # Try to detect NVIDIA GPU
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    parts = lines[0].split(',')
                    info["gpu_available"] = True
                    info["gpu_name"] = parts[0].strip()
                    info["vram_gb"] = round(float(parts[1].strip()) / 1024, 1)
        except:
            pass
        
        return info
    
    @staticmethod
    def get_recommended_tier(hardware_info: Dict[str, Any]) -> str:
        """Get recommended model tier based on hardware."""
        vram = hardware_info.get("vram_gb", 0)
        ram = hardware_info.get("ram_gb", 0)
        
        if vram >= 16:
            return "heavy"
        elif vram >= 8:
            return "medium"
        elif vram >= 4 or ram >= 32:
            return "light"
        else:
            return "minimal"
    
    @staticmethod
    def display_hardware_info(info: Dict[str, Any]):
        """Display hardware information in a nice table."""
        table = Table(title="💻 System Hardware", show_header=True, header_style="bold cyan")
        table.add_column("Component", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("RAM", f"{info['ram_gb']} GB (Available: {info['ram_available_gb']} GB)")
        table.add_row("CPU", f"{info['cpu_cores']} cores / {info['cpu_threads']} threads")
        
        if info["gpu_available"]:
            table.add_row("GPU", f"✓ {info['gpu_name']}")
            table.add_row("VRAM", f"{info['vram_gb']} GB")
        else:
            table.add_row("GPU", "❌ Not detected (CPU-only mode)")
        
        console.print(table)


class ModelManager:
    """Manages Ollama model installation and configuration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.ollama_url = self.config.get("ollama", {}).get("base_url", "http://localhost:11434")
        
    def check_ollama_running(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.ok
        except:
            return False
    
    def start_ollama(self) -> bool:
        """Attempt to start Ollama."""
        try:
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            import time
            time.sleep(3)
            return self.check_ollama_running()
        except:
            return False
    
    def get_installed_models(self) -> List[str]:
        """Get list of installed Ollama models."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.ok:
                data = response.json()
                return [m["name"].split(":")[0] for m in data.get("models", [])]
        except:
            pass
        return []
    
    def install_model(self, model_name: str, progress_callback=None) -> bool:
        """Install an Ollama model."""
        console.print(f"[cyan]Pulling model: {model_name}...[/cyan]")
        
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            for line in process.stdout:
                if progress_callback:
                    progress_callback(line.strip())
                else:
                    # Parse progress from Ollama output
                    if "pulling" in line.lower() or "%" in line:
                        console.print(f"  [dim]{line.strip()}[/dim]", end="\r")
            
            process.wait()
            console.print()  # New line after progress
            return process.returncode == 0
            
        except Exception as e:
            console.print(f"[red]Error installing model: {e}[/red]")
            return False
    
    def uninstall_model(self, model_name: str) -> bool:
        """Uninstall an Ollama model."""
        try:
            result = subprocess.run(
                ["ollama", "rm", model_name],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def get_model_catalog(self, category: str = None, tier: str = None) -> List[ModelInfo]:
        """Get models from catalog, optionally filtered."""
        installed = self.get_installed_models()
        
        models = []
        categories = [category] if category else MODEL_CATALOG.keys()
        
        for cat in categories:
            for model in MODEL_CATALOG.get(cat, []):
                # Check if installed
                model.is_installed = any(model.name.split(":")[0] in m for m in installed)
                
                # Filter by tier
                if tier:
                    if tier == "minimal" and model.vram_required > 3:
                        continue
                    elif tier == "light" and model.vram_required > 6:
                        continue
                    elif tier == "medium" and model.vram_required > 12:
                        continue
                
                models.append(model)
        
        return models
    
    def display_models(self, category: str = None, tier: str = None):
        """Display available models in a formatted table."""
        models = self.get_model_catalog(category, tier)
        
        if not models:
            console.print("[yellow]No models found for the specified criteria.[/yellow]")
            return
        
        # Group by category
        for cat in ["vision", "analyzer"]:
            cat_models = [m for m in models if m.category == cat]
            if not cat_models:
                continue
            
            title = "👁️ Vision Models" if cat == "vision" else "🧠 Analyzer Models"
            table = Table(title=title, show_header=True, header_style="bold magenta")
            table.add_column("#", style="cyan", width=3)
            table.add_column("Model", style="green", width=20)
            table.add_column("Size", width=8)
            table.add_column("VRAM", width=8)
            table.add_column("Description", width=40)
            table.add_column("Status", width=12)
            
            for i, model in enumerate(cat_models, 1):
                status = "[green]✓ Installed[/green]" if model.is_installed else "[dim]Not installed[/dim]"
                table.add_row(
                    str(i),
                    model.display_name,
                    f"{model.size_gb} GB",
                    f"{model.vram_required} GB",
                    model.description[:40] + "..." if len(model.description) > 40 else model.description,
                    status
                )
            
            console.print(table)
            console.print()


class TrainedModelManager:
    """Manages fine-tuned and pre-trained models."""
    
    def __init__(self, models_dir: str = "models", datasets_dir: str = "datasets", 
                 tokenizers_dir: str = "tokenizers"):
        self.models_dir = Path(models_dir)
        self.datasets_dir = Path(datasets_dir)
        self.tokenizers_dir = Path(tokenizers_dir)
    
    def list_trained_models(self) -> List[Dict[str, Any]]:
        """List all trained/fine-tuned models."""
        models = []
        
        if not self.models_dir.exists():
            return models
        
        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir():
                # Check for fine-tuned adapter
                adapter_path = model_dir / "final_adapter"
                is_adapter = adapter_path.exists()
                
                # Check for pre-trained model
                pretrain_config = model_dir / "config.json"
                is_pretrained = pretrain_config.exists() and not is_adapter
                
                if is_adapter or is_pretrained:
                    # Try to read config
                    config_path = adapter_path / "adapter_config.json" if is_adapter else pretrain_config
                    base_model = "Custom" if is_pretrained else "Unknown"
                    
                    if config_path.exists():
                        try:
                            with open(config_path) as f:
                                config = json.load(f)
                                if is_adapter:
                                    base_model = config.get("base_model_name_or_path", "Unknown")
                                else:
                                    base_model = f"Custom ({config.get('hidden_size', '?')}d)"
                        except:
                            pass
                    
                    # Calculate size
                    target_path = adapter_path if is_adapter else model_dir
                    try:
                        size_bytes = sum(f.stat().st_size for f in target_path.rglob("*") if f.is_file())
                        size_mb = size_bytes / (1024**2)
                    except:
                        size_mb = 0
                    
                    # Check for checkpoints
                    checkpoints = list(model_dir.glob("checkpoint-*"))
                    
                    models.append({
                        "name": model_dir.name,
                        "path": str(target_path),
                        "base_model": base_model,
                        "size_mb": size_mb,
                        "type": "adapter" if is_adapter else "pretrained",
                        "checkpoints": len(checkpoints),
                        "created": model_dir.stat().st_mtime if model_dir.exists() else 0
                    })
        
        # Sort by creation time (newest first)
        models.sort(key=lambda x: x.get("created", 0), reverse=True)
        return models
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific model."""
        model_path = self.models_dir / model_name
        
        if not model_path.exists():
            return None
        
        info = {
            "name": model_name,
            "path": str(model_path),
            "exists": True,
        }
        
        # Check for adapter
        adapter_path = model_path / "final_adapter"
        if adapter_path.exists():
            info["type"] = "fine-tuned adapter"
            info["adapter_path"] = str(adapter_path)
            
            config_path = adapter_path / "adapter_config.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    info["base_model"] = config.get("base_model_name_or_path", "Unknown")
                    info["lora_rank"] = config.get("r", "Unknown")
                    info["lora_alpha"] = config.get("lora_alpha", "Unknown")
        else:
            # Check for pretrained model
            config_path = model_path / "config.json"
            if config_path.exists():
                info["type"] = "pre-trained model"
                with open(config_path) as f:
                    config = json.load(f)
                    info["hidden_size"] = config.get("hidden_size", "Unknown")
                    info["num_layers"] = config.get("num_hidden_layers", "Unknown")
                    info["vocab_size"] = config.get("vocab_size", "Unknown")
        
        # Calculate size
        try:
            size_bytes = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file())
            info["size_mb"] = round(size_bytes / (1024**2), 2)
            info["size_gb"] = round(size_bytes / (1024**3), 2)
        except:
            info["size_mb"] = 0
        
        # List checkpoints
        checkpoints = sorted(model_path.glob("checkpoint-*"))
        info["checkpoints"] = [cp.name for cp in checkpoints]
        
        # List files
        info["files"] = [f.name for f in model_path.iterdir() if f.is_file()][:10]
        
        return info
    
    def display_trained_models(self):
        """Display trained models in a table."""
        models = self.list_trained_models()
        
        if not models:
            console.print("[yellow]No fine-tuned models found.[/yellow]")
            console.print("[dim]Train a model with: saara train[/dim]")
            return
        
        table = Table(title="🎯 Trained Models", show_header=True, header_style="bold cyan")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Name", style="green")
        table.add_column("Type", style="magenta")
        table.add_column("Base Model", style="yellow")
        table.add_column("Size", width=10)
        table.add_column("Checkpoints", width=5)
        
        for i, model in enumerate(models, 1):
            model_type = "🔧 Adapter" if model["type"] == "adapter" else "🏗️ Pretrained"
            table.add_row(
                str(i),
                model["name"],
                model_type,
                model["base_model"].split("/")[-1][:20],
                f"{model['size_mb']:.1f} MB",
                str(model["checkpoints"])
            )
        
        console.print(table)
    
    def display_model_info(self, model_name: str):
        """Display detailed model information."""
        info = self.get_model_info(model_name)
        
        if not info:
            console.print(f"[red]Model not found: {model_name}[/red]")
            return
        
        console.print(Panel(
            f"[bold cyan]{info['name']}[/bold cyan]\n\n"
            f"[green]Type:[/green] {info.get('type', 'Unknown')}\n"
            f"[green]Path:[/green] {info['path']}\n"
            f"[green]Size:[/green] {info.get('size_mb', 0):.1f} MB ({info.get('size_gb', 0):.2f} GB)\n\n"
            + (f"[yellow]Base Model:[/yellow] {info.get('base_model', 'N/A')}\n" if 'base_model' in info else "")
            + (f"[yellow]LoRA Rank:[/yellow] {info.get('lora_rank', 'N/A')}\n" if 'lora_rank' in info else "")
            + (f"[yellow]Hidden Size:[/yellow] {info.get('hidden_size', 'N/A')}\n" if 'hidden_size' in info else "")
            + (f"[yellow]Layers:[/yellow] {info.get('num_layers', 'N/A')}\n" if 'num_layers' in info else "")
            + f"\n[dim]Checkpoints:[/dim] {len(info.get('checkpoints', []))}"
            + (f"\n  {', '.join(info.get('checkpoints', [])[:5])}" if info.get('checkpoints') else ""),
            title="📋 Model Details",
            border_style="cyan"
        ))
    
    def delete_trained_model(self, model_name: str, include_checkpoints: bool = True) -> bool:
        """Delete a fine-tuned model."""
        import shutil
        model_path = self.models_dir / model_name
        
        if model_path.exists():
            shutil.rmtree(model_path)
            console.print(f"[green]✓ Deleted model: {model_name}[/green]")
            return True
        
        console.print(f"[red]Model not found: {model_name}[/red]")
        return False
    
    def delete_checkpoint(self, model_name: str, checkpoint_name: str) -> bool:
        """Delete a specific checkpoint from a model."""
        import shutil
        checkpoint_path = self.models_dir / model_name / checkpoint_name
        
        if checkpoint_path.exists():
            shutil.rmtree(checkpoint_path)
            console.print(f"[green]✓ Deleted checkpoint: {checkpoint_name}[/green]")
            return True
        return False
    
    def clear_all_models(self, confirm: bool = False) -> int:
        """Delete all trained models. Returns count of deleted models."""
        import shutil
        
        if not self.models_dir.exists():
            return 0
        
        models = self.list_trained_models()
        
        if not models:
            console.print("[yellow]No models to delete.[/yellow]")
            return 0
        
        if not confirm:
            console.print(f"[red]This will delete {len(models)} models![/red]")
            return 0
        
        count = 0
        for model in models:
            model_path = self.models_dir / model["name"]
            if model_path.exists():
                shutil.rmtree(model_path)
                count += 1
                console.print(f"  [dim]Deleted: {model['name']}[/dim]")
        
        console.print(f"[green]✓ Deleted {count} models[/green]")
        return count
    
    def clear_all_checkpoints(self, model_name: str = None) -> int:
        """Clear all checkpoints, keeping only final model."""
        import shutil
        
        if not self.models_dir.exists():
            return 0
        
        count = 0
        
        if model_name:
            # Clear checkpoints for specific model
            model_path = self.models_dir / model_name
            if model_path.exists():
                for checkpoint in model_path.glob("checkpoint-*"):
                    shutil.rmtree(checkpoint)
                    count += 1
        else:
            # Clear all checkpoints
            for model_dir in self.models_dir.iterdir():
                if model_dir.is_dir():
                    for checkpoint in model_dir.glob("checkpoint-*"):
                        shutil.rmtree(checkpoint)
                        count += 1
        
        if count > 0:
            console.print(f"[green]✓ Cleared {count} checkpoints[/green]")
        return count
    
    def clear_datasets(self, confirm: bool = False) -> int:
        """Clear all generated datasets."""
        import shutil
        
        if not self.datasets_dir.exists():
            return 0
        
        files = list(self.datasets_dir.glob("*.jsonl")) + list(self.datasets_dir.glob("*.json"))
        
        if not files:
            console.print("[yellow]No datasets to delete.[/yellow]")
            return 0
        
        if not confirm:
            console.print(f"[red]This will delete {len(files)} dataset files![/red]")
            return 0
        
        count = 0
        for f in files:
            f.unlink()
            count += 1
        
        console.print(f"[green]✓ Deleted {count} dataset files[/green]")
        return count
    
    def clear_tokenizers(self, confirm: bool = False) -> int:
        """Clear all custom tokenizers."""
        import shutil
        
        if not self.tokenizers_dir.exists():
            return 0
        
        tokenizers = [d for d in self.tokenizers_dir.iterdir() if d.is_dir()]
        
        if not tokenizers:
            console.print("[yellow]No tokenizers to delete.[/yellow]")
            return 0
        
        if not confirm:
            console.print(f"[red]This will delete {len(tokenizers)} tokenizers![/red]")
            return 0
        
        count = 0
        for t in tokenizers:
            shutil.rmtree(t)
            count += 1
        
        console.print(f"[green]✓ Deleted {count} tokenizers[/green]")
        return count
    
    def reset_all(self, confirm: bool = False) -> Dict[str, int]:
        """Reset everything - delete all models, datasets, and tokenizers."""
        if not confirm:
            console.print("[red]⚠️ This will delete ALL trained models, datasets, and tokenizers![/red]")
            return {"models": 0, "datasets": 0, "tokenizers": 0}
        
        results = {
            "models": self.clear_all_models(confirm=True),
            "datasets": self.clear_datasets(confirm=True),
            "tokenizers": self.clear_tokenizers(confirm=True),
        }
        
        console.print(Panel(
            f"[green]Reset complete![/green]\n\n"
            f"Deleted models: {results['models']}\n"
            f"Deleted datasets: {results['datasets']}\n"
            f"Deleted tokenizers: {results['tokenizers']}",
            title="🔄 Factory Reset",
            border_style="green"
        ))
        
        return results
    
    def get_storage_usage(self) -> Dict[str, float]:
        """Get storage usage for models, datasets, and tokenizers."""
        usage = {}
        
        for name, path in [("models", self.models_dir), 
                           ("datasets", self.datasets_dir),
                           ("tokenizers", self.tokenizers_dir)]:
            if path.exists():
                try:
                    size_bytes = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
                    usage[name] = round(size_bytes / (1024**3), 2)  # GB
                except:
                    usage[name] = 0
            else:
                usage[name] = 0
        
        usage["total"] = sum(usage.values())
        return usage
    
    def display_storage_usage(self):
        """Display storage usage summary."""
        usage = self.get_storage_usage()
        
        table = Table(title="💾 Storage Usage", show_header=True, header_style="bold cyan")
        table.add_column("Category", style="cyan")
        table.add_column("Size", style="green", justify="right")
        
        table.add_row("Models", f"{usage.get('models', 0):.2f} GB")
        table.add_row("Datasets", f"{usage.get('datasets', 0):.2f} GB")
        table.add_row("Tokenizers", f"{usage.get('tokenizers', 0):.2f} GB")
        table.add_row("─" * 15, "─" * 10)
        table.add_row("[bold]Total[/bold]", f"[bold]{usage.get('total', 0):.2f} GB[/bold]")
        
        console.print(table)
    
    def prepare_for_retrain(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Prepare model for retraining from scratch.
        Returns info needed to retrain, then deletes the old model.
        """
        info = self.get_model_info(model_name)
        
        if not info:
            return None
        
        # Save retrain configuration
        retrain_config = {
            "original_name": model_name,
            "base_model": info.get("base_model"),
            "type": info.get("type"),
            "lora_rank": info.get("lora_rank"),
            "lora_alpha": info.get("lora_alpha"),
        }
        
        return retrain_config

