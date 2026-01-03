"""
Pre-training Module for SAARA
Build and train language models from scratch.

© 2024-2025 Kilani Sai Nikhil. All Rights Reserved.
"""

import logging
import json
import math
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict

import torch
from datasets import load_dataset, concatenate_datasets
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    PreTrainedTokenizerFast,
)
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, processors, decoders
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
logger = logging.getLogger(__name__)


# ============================================================================
# Model Architecture Configurations
# ============================================================================

@dataclass
class ModelArchitecture:
    """Defines a model architecture configuration."""
    name: str
    display_name: str
    hidden_size: int
    num_hidden_layers: int
    num_attention_heads: int
    intermediate_size: int
    vocab_size: int = 32000
    max_position_embeddings: int = 2048
    num_key_value_heads: Optional[int] = None  # For GQA
    rope_theta: float = 10000.0
    rms_norm_eps: float = 1e-6
    tie_word_embeddings: bool = False
    estimated_params: str = ""
    min_vram_gb: float = 4.0
    description: str = ""
    
    def to_config_dict(self) -> Dict[str, Any]:
        """Convert to HuggingFace config format."""
        config = {
            "hidden_size": self.hidden_size,
            "num_hidden_layers": self.num_hidden_layers,
            "num_attention_heads": self.num_attention_heads,
            "intermediate_size": self.intermediate_size,
            "vocab_size": self.vocab_size,
            "max_position_embeddings": self.max_position_embeddings,
            "rms_norm_eps": self.rms_norm_eps,
            "tie_word_embeddings": self.tie_word_embeddings,
            "rope_theta": self.rope_theta,
            "use_cache": True,
            "bos_token_id": 1,
            "eos_token_id": 2,
            "pad_token_id": 0,
        }
        if self.num_key_value_heads:
            config["num_key_value_heads"] = self.num_key_value_heads
        return config


# Pre-defined architectures (LLaMA-style)
ARCHITECTURES = {
    "nano": ModelArchitecture(
        name="nano",
        display_name="Nano (15M)",
        hidden_size=256,
        num_hidden_layers=6,
        num_attention_heads=4,
        intermediate_size=512,
        vocab_size=32000,
        max_position_embeddings=512,
        estimated_params="~15M",
        min_vram_gb=2.0,
        description="Tiny model for testing and learning. Trains fast on CPU."
    ),
    "micro": ModelArchitecture(
        name="micro",
        display_name="Micro (50M)",
        hidden_size=512,
        num_hidden_layers=8,
        num_attention_heads=8,
        intermediate_size=1024,
        vocab_size=32000,
        max_position_embeddings=1024,
        estimated_params="~50M",
        min_vram_gb=4.0,
        description="Small model for experimentation. Fast training on single GPU."
    ),
    "mini": ModelArchitecture(
        name="mini",
        display_name="Mini (125M)",
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        intermediate_size=2048,
        vocab_size=32000,
        max_position_embeddings=2048,
        estimated_params="~125M",
        min_vram_gb=6.0,
        description="GPT-2 Small equivalent. Good for domain-specific pre-training."
    ),
    "small": ModelArchitecture(
        name="small",
        display_name="Small (350M)",
        hidden_size=1024,
        num_hidden_layers=24,
        num_attention_heads=16,
        intermediate_size=2816,
        vocab_size=32000,
        max_position_embeddings=2048,
        estimated_params="~350M",
        min_vram_gb=8.0,
        description="Medium capacity. Suitable for specialized tasks."
    ),
    "base": ModelArchitecture(
        name="base",
        display_name="Base (1B)",
        hidden_size=2048,
        num_hidden_layers=24,
        num_attention_heads=16,
        num_key_value_heads=8,  # GQA
        intermediate_size=5504,
        vocab_size=32000,
        max_position_embeddings=4096,
        estimated_params="~1B",
        min_vram_gb=16.0,
        description="Production-ready size. Requires good GPU (16GB+ VRAM)."
    ),
    "large": ModelArchitecture(
        name="large",
        display_name="Large (3B)",
        hidden_size=3200,
        num_hidden_layers=26,
        num_attention_heads=32,
        num_key_value_heads=8,
        intermediate_size=8640,
        vocab_size=32000,
        max_position_embeddings=4096,
        estimated_params="~3B",
        min_vram_gb=24.0,
        description="High capacity model. Requires 24GB+ VRAM or multi-GPU."
    ),
}


# ============================================================================
# Custom Tokenizer Trainer
# ============================================================================

class TokenizerTrainer:
    """Trains a custom BPE tokenizer on domain-specific data."""
    
    def __init__(self, vocab_size: int = 32000):
        self.vocab_size = vocab_size
        
    def train(self, data_files: List[str], output_dir: str) -> str:
        """
        Train a BPE tokenizer on the given data files.
        
        Args:
            data_files: List of text files to train on
            output_dir: Directory to save the tokenizer
            
        Returns:
            Path to the saved tokenizer
        """
        console.print("[bold cyan]🔤 Training Custom Tokenizer...[/bold cyan]")
        
        # Initialize a BPE tokenizer
        tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
        
        # Pre-tokenizer (splits on whitespace and punctuation)
        tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
        
        # Decoder
        tokenizer.decoder = decoders.ByteLevel()
        
        # Post-processor for adding special tokens
        tokenizer.post_processor = processors.ByteLevel(trim_offsets=False)
        
        # BPE trainer
        trainer = trainers.BpeTrainer(
            vocab_size=self.vocab_size,
            min_frequency=2,
            special_tokens=["<pad>", "<s>", "</s>", "<unk>"],
            show_progress=True,
        )
        
        # Train
        console.print(f"  Training on {len(data_files)} file(s)...")
        tokenizer.train(files=data_files, trainer=trainer)
        
        # Save
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        tokenizer_path = output_path / "tokenizer.json"
        tokenizer.save(str(tokenizer_path))
        
        # Create tokenizer config for HuggingFace compatibility
        config = {
            "add_bos_token": True,
            "add_eos_token": False,
            "bos_token": "<s>",
            "eos_token": "</s>",
            "pad_token": "<pad>",
            "unk_token": "<unk>",
            "model_max_length": 2048,
            "tokenizer_class": "PreTrainedTokenizerFast",
        }
        
        with open(output_path / "tokenizer_config.json", "w") as f:
            json.dump(config, f, indent=2)
            
        # Create special tokens map
        special_tokens = {
            "bos_token": "<s>",
            "eos_token": "</s>",
            "unk_token": "<unk>",
            "pad_token": "<pad>",
        }
        with open(output_path / "special_tokens_map.json", "w") as f:
            json.dump(special_tokens, f, indent=2)
        
        console.print(f"[green]✅ Tokenizer saved to {output_path}[/green]")
        console.print(f"   Vocabulary size: {tokenizer.get_vocab_size()}")
        
        return str(output_path)


# ============================================================================
# Pre-training Trainer
# ============================================================================

class PreTrainer:
    """
    Pre-trains a language model from scratch.
    """
    
    def __init__(self, 
                 architecture: str = "micro",
                 model_name: str = "my-model",
                 output_dir: str = "models",
                 config: Dict[str, Any] = None):
        self.config = config or {}
        self.model_name = model_name
        self.output_dir = Path(output_dir) / model_name
        
        # Get architecture
        if architecture in ARCHITECTURES:
            self.arch = ARCHITECTURES[architecture]
        else:
            raise ValueError(f"Unknown architecture: {architecture}. Choose from: {list(ARCHITECTURES.keys())}")
        
        # Training hyperparameters
        self.train_params = {
            "learning_rate": 3e-4,
            "per_device_train_batch_size": 8,
            "gradient_accumulation_steps": 4,
            "num_train_epochs": 1,
            "max_seq_length": min(1024, self.arch.max_position_embeddings),
            "logging_steps": 10,
            "save_steps": 500,
            "warmup_ratio": 0.1,
            "weight_decay": 0.1,
            "lr_scheduler_type": "cosine",
        }
        
    def prepare_data(self, data_path: str) -> Any:
        """Load and prepare dataset for pre-training."""
        console.print(f"[bold yellow]📂 Loading data from: {data_path}[/bold yellow]")
        
        path_obj = Path(data_path)
        
        if path_obj.is_file():
            if data_path.endswith(".jsonl") or data_path.endswith(".json"):
                dataset = load_dataset("json", data_files=data_path, split="train")
            else:
                dataset = load_dataset("text", data_files=data_path, split="train")
        elif path_obj.is_dir():
            # Load all text files
            txt_files = list(path_obj.glob("**/*.txt"))
            md_files = list(path_obj.glob("**/*.md"))
            jsonl_files = list(path_obj.glob("**/*.jsonl"))
            
            datasets = []
            if txt_files or md_files:
                all_text = [str(f) for f in txt_files + md_files]
                if all_text:
                    datasets.append(load_dataset("text", data_files=all_text, split="train"))
                    
            if jsonl_files:
                for jf in jsonl_files:
                    try:
                        ds = load_dataset("json", data_files=str(jf), split="train")
                        datasets.append(ds)
                    except:
                        pass
                        
            if datasets:
                dataset = concatenate_datasets(datasets)
            else:
                raise ValueError("No valid data files found in directory")
        else:
            raise ValueError(f"Data path not found: {data_path}")
            
        console.print(f"[green]✅ Loaded {len(dataset)} samples[/green]")
        return dataset
    
    def create_model(self, tokenizer_path: Optional[str] = None) -> tuple:
        """Create model and tokenizer from scratch."""
        console.print(f"\n[bold cyan]🏗️ Creating {self.arch.display_name} Model...[/bold cyan]")
        
        # Load or create tokenizer
        if tokenizer_path:
            console.print(f"  Loading tokenizer from: {tokenizer_path}")
            tokenizer = PreTrainedTokenizerFast.from_pretrained(tokenizer_path)
        else:
            # Use LLaMA tokenizer as base
            console.print("  Using default LLaMA tokenizer")
            tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        
        tokenizer.pad_token = tokenizer.eos_token
        
        # Update vocab size in architecture
        self.arch.vocab_size = len(tokenizer)
        
        # Create model config
        config_dict = self.arch.to_config_dict()
        config_dict["architectures"] = ["LlamaForCausalLM"]
        config_dict["model_type"] = "llama"
        
        config = AutoConfig.for_model("llama", **config_dict)
        
        # Initialize model with random weights
        console.print("  Initializing model with random weights...")
        model = AutoModelForCausalLM.from_config(config)
        
        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        console.print(f"[green]✅ Model created![/green]")
        console.print(f"   Total parameters: {total_params:,} ({total_params/1e6:.1f}M)")
        console.print(f"   Trainable: {trainable_params:,}")
        
        return model, tokenizer
    
    def pretrain(self, 
                 data_path: str, 
                 tokenizer_path: Optional[str] = None,
                 resume_from: Optional[str] = None):
        """
        Run pre-training from scratch.
        
        Args:
            data_path: Path to training data (text files or JSONL)
            tokenizer_path: Path to custom tokenizer (optional)
            resume_from: Path to checkpoint to resume from (optional)
        """
        from rich.table import Table
        
        # Display config
        config_table = Table(title="🚀 Pre-training Configuration", show_header=True, header_style="bold cyan")
        config_table.add_column("Parameter", style="green")
        config_table.add_column("Value", style="yellow")
        
        config_table.add_row("Model Name", self.model_name)
        config_table.add_row("Architecture", self.arch.display_name)
        config_table.add_row("Parameters", self.arch.estimated_params)
        config_table.add_row("Hidden Size", str(self.arch.hidden_size))
        config_table.add_row("Layers", str(self.arch.num_hidden_layers))
        config_table.add_row("Attention Heads", str(self.arch.num_attention_heads))
        config_table.add_row("Max Sequence Length", str(self.train_params["max_seq_length"]))
        config_table.add_row("Learning Rate", str(self.train_params["learning_rate"]))
        config_table.add_row("Output Directory", str(self.output_dir))
        
        console.print(config_table)
        console.print()
        
        # Load data
        dataset = self.prepare_data(data_path)
        
        # Create model and tokenizer
        model, tokenizer = self.create_model(tokenizer_path)
        
        # Tokenize dataset
        console.print("\n[bold yellow]🔄 Tokenizing dataset...[/bold yellow]")
        
        max_length = self.train_params["max_seq_length"]
        
        def tokenize_function(examples):
            # Handle different dataset formats
            if "text" in examples:
                texts = examples["text"]
            elif "content" in examples:
                texts = examples["content"]
            elif "conversations" in examples:
                # ShareGPT format - concatenate conversations
                texts = []
                for conv in examples["conversations"]:
                    if isinstance(conv, list):
                        text = " ".join([m.get("value", m.get("content", "")) for m in conv])
                        texts.append(text)
                    else:
                        texts.append(str(conv))
            else:
                # Try first column
                first_col = list(examples.keys())[0]
                texts = [str(t) for t in examples[first_col]]
            
            return tokenizer(
                texts,
                truncation=True,
                max_length=max_length,
                padding="max_length",
                return_special_tokens_mask=True,
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
            desc="Tokenizing",
        )
        
        console.print(f"[green]✅ Dataset tokenized: {len(tokenized_dataset)} samples[/green]")
        
        # Data collator for CLM
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,  # Causal LM, not masked
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            overwrite_output_dir=True,
            num_train_epochs=self.train_params["num_train_epochs"],
            per_device_train_batch_size=self.train_params["per_device_train_batch_size"],
            gradient_accumulation_steps=self.train_params["gradient_accumulation_steps"],
            learning_rate=self.train_params["learning_rate"],
            weight_decay=self.train_params["weight_decay"],
            warmup_ratio=self.train_params["warmup_ratio"],
            lr_scheduler_type=self.train_params["lr_scheduler_type"],
            logging_steps=self.train_params["logging_steps"],
            save_steps=self.train_params["save_steps"],
            save_total_limit=3,
            fp16=torch.cuda.is_available(),
            bf16=False,
            gradient_checkpointing=True,
            report_to="tensorboard",
            dataloader_num_workers=0,
            remove_unused_columns=False,
        )
        
        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
            tokenizer=tokenizer,
        )
        
        # Train
        console.print("\n[bold green]▶️ Starting pre-training...[/bold green]\n")
        trainer.train(resume_from_checkpoint=resume_from)
        
        # Save final model
        final_path = self.output_dir / "final"
        console.print(f"\n[bold cyan]💾 Saving model to {final_path}...[/bold cyan]")
        trainer.save_model(str(final_path))
        tokenizer.save_pretrained(str(final_path))
        
        # Save architecture info
        arch_info = {
            "name": self.model_name,
            "architecture": self.arch.name,
            "config": asdict(self.arch),
            "training_params": self.train_params,
        }
        with open(final_path / "saara_config.json", "w") as f:
            json.dump(arch_info, f, indent=2)
        
        # Success message
        console.print(Panel.fit(
            f"[bold green]✅ Pre-training Complete![/bold green]\n\n"
            f"[yellow]Model saved to:[/yellow] {final_path}\n\n"
            f"[yellow]To use this model:[/yellow]\n"
            f"  from transformers import AutoModelForCausalLM\n"
            f"  model = AutoModelForCausalLM.from_pretrained(\"{final_path}\")\n\n"
            f"[yellow]To fine-tune:[/yellow]\n"
            f"  saara train  # Select your custom model",
            title="🎉 Success",
            border_style="green"
        ))
        
        return str(final_path)


# ============================================================================
# Model Tester / Evaluator
# ============================================================================

class PretrainedModelTester:
    """Test and evaluate pre-trained models."""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        
    def load(self):
        """Load the model for testing."""
        console.print(f"[bold cyan]Loading model from {self.model_path}...[/bold cyan]")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        console.print("[green]✅ Model loaded![/green]")
        
    def generate(self, prompt: str, max_length: int = 100) -> str:
        """Generate text from a prompt."""
        if self.model is None:
            self.load()
            
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
            
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.pad_token_id,
            )
            
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def calculate_perplexity(self, text: str) -> float:
        """Calculate perplexity on given text."""
        if self.model is None:
            self.load()
            
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
            
        with torch.no_grad():
            outputs = self.model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
            
        return math.exp(loss.item())
    
    def interactive_test(self):
        """Run interactive testing session."""
        console.print(Panel.fit(
            "[bold cyan]Interactive Model Testing[/bold cyan]\n\n"
            "Enter prompts to test your model.\n"
            "Type 'quit' to exit, 'perplexity <text>' to calculate perplexity.",
            border_style="cyan"
        ))
        
        self.load()
        
        while True:
            prompt = console.input("\n[bold green]Prompt>[/bold green] ")
            
            if prompt.lower() == "quit":
                break
            elif prompt.lower().startswith("perplexity "):
                text = prompt[11:]
                ppl = self.calculate_perplexity(text)
                console.print(f"[yellow]Perplexity: {ppl:.2f}[/yellow]")
            else:
                console.print("[dim]Generating...[/dim]")
                output = self.generate(prompt)
                console.print(f"\n[cyan]{output}[/cyan]")


# ============================================================================
# Model Expander - Progressive Scaling
# ============================================================================

class ModelExpander:
    """
    Enables progressive model scaling - start small and expand over time.
    
    This allows users to:
    1. Start training with a small model (e.g., 15M params)
    2. After some training, expand to a larger architecture (e.g., 50M)
    3. The larger model inherits knowledge from the smaller one
    
    Techniques used:
    - Weight interpolation for shared dimensions
    - Smart initialization for new parameters
    - Preserves learned embeddings where possible
    """
    
    def __init__(self, source_model_path: str, target_architecture: str):
        self.source_path = Path(source_model_path)
        self.target_arch_name = target_architecture
        
        if target_architecture not in ARCHITECTURES:
            raise ValueError(f"Unknown target architecture: {target_architecture}")
        
        self.target_arch = ARCHITECTURES[target_architecture]
        
    def expand(self, output_path: str = None) -> str:
        """
        Expand the source model to the target architecture.
        
        Returns:
            Path to the expanded model
        """
        console.print(Panel.fit(
            f"[bold cyan]📈 Model Expansion[/bold cyan]\n\n"
            f"Expanding model to {self.target_arch.display_name}",
            border_style="cyan"
        ))
        
        # Load source model and config
        console.print("\n[bold]Step 1: Loading source model...[/bold]")
        
        source_config_path = self.source_path / "saara_config.json"
        if not source_config_path.exists():
            raise ValueError(f"Source model config not found: {source_config_path}")
        
        with open(source_config_path) as f:
            source_info = json.load(f)
        
        source_arch_name = source_info.get("architecture", "unknown")
        console.print(f"  Source: {source_arch_name} → Target: {self.target_arch_name}")
        
        # Verify expansion is valid (target should be larger)
        arch_order = list(ARCHITECTURES.keys())
        if source_arch_name in arch_order and self.target_arch_name in arch_order:
            source_idx = arch_order.index(source_arch_name)
            target_idx = arch_order.index(self.target_arch_name)
            if target_idx <= source_idx:
                console.print("[yellow]⚠ Warning: Target architecture is not larger than source.[/yellow]")
                console.print("[dim]Expansion typically works best when scaling up.[/dim]")
        
        # Load the source model
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        console.print("  Loading source weights...")
        source_model = AutoModelForCausalLM.from_pretrained(
            str(self.source_path),
            torch_dtype=torch.float32,  # Full precision for manipulation
        )
        source_tokenizer = AutoTokenizer.from_pretrained(str(self.source_path))
        
        source_state = source_model.state_dict()
        source_hidden = source_model.config.hidden_size
        source_layers = source_model.config.num_hidden_layers
        
        console.print(f"  Source: hidden={source_hidden}, layers={source_layers}")
        
        # Create target model
        console.print("\n[bold]Step 2: Creating target architecture...[/bold]")
        
        target_config_dict = self.target_arch.to_config_dict()
        target_config_dict["vocab_size"] = len(source_tokenizer)  # Keep same vocab
        target_config_dict["architectures"] = ["LlamaForCausalLM"]
        target_config_dict["model_type"] = "llama"
        
        target_config = AutoConfig.for_model("llama", **target_config_dict)
        target_model = AutoModelForCausalLM.from_config(target_config)
        
        target_hidden = target_config.hidden_size
        target_layers = target_config.num_hidden_layers
        
        console.print(f"  Target: hidden={target_hidden}, layers={target_layers}")
        
        # Transfer weights
        console.print("\n[bold]Step 3: Transferring knowledge...[/bold]")
        
        target_state = target_model.state_dict()
        transferred = 0
        interpolated = 0
        new_init = 0
        
        for name, target_param in target_state.items():
            if name in source_state:
                source_param = source_state[name]
                
                if source_param.shape == target_param.shape:
                    # Direct copy - same shape
                    target_state[name] = source_param.clone()
                    transferred += 1
                elif len(source_param.shape) == len(target_param.shape):
                    # Interpolate - different sizes
                    try:
                        target_state[name] = self._interpolate_weights(
                            source_param, target_param.shape
                        )
                        interpolated += 1
                    except Exception as e:
                        logger.debug(f"Could not interpolate {name}: {e}")
                        new_init += 1
                else:
                    new_init += 1
            else:
                new_init += 1
        
        # Load transferred state
        target_model.load_state_dict(target_state)
        
        console.print(f"  [green]✓ Direct transfer: {transferred} tensors[/green]")
        console.print(f"  [yellow]↔ Interpolated: {interpolated} tensors[/yellow]")
        console.print(f"  [dim]★ New initialization: {new_init} tensors[/dim]")
        
        # Save expanded model
        console.print("\n[bold]Step 4: Saving expanded model...[/bold]")
        
        if output_path is None:
            source_name = source_info.get("name", "model")
            output_path = self.source_path.parent / f"{source_name}-expanded-{self.target_arch_name}"
        
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        target_model.save_pretrained(str(output_path))
        source_tokenizer.save_pretrained(str(output_path))
        
        # Save new config
        expanded_config = {
            "name": f"{source_info.get('name', 'model')}-{self.target_arch_name}",
            "architecture": self.target_arch_name,
            "config": {
                "estimated_params": self.target_arch.estimated_params,
                "hidden_size": target_hidden,
                "num_hidden_layers": target_layers,
            },
            "expanded_from": {
                "path": str(self.source_path),
                "architecture": source_arch_name,
            },
            "expansion_stats": {
                "transferred": transferred,
                "interpolated": interpolated,
                "new_init": new_init,
            }
        }
        
        with open(output_path / "saara_config.json", "w") as f:
            json.dump(expanded_config, f, indent=2)
        
        console.print(f"  [green]✓ Saved to: {output_path}[/green]")
        
        # Summary
        console.print(Panel.fit(
            f"[bold green]✅ Model Expansion Complete![/bold green]\n\n"
            f"[yellow]From:[/yellow] {source_arch_name} ({source_info.get('config', {}).get('estimated_params', '?')})\n"
            f"[yellow]To:[/yellow] {self.target_arch_name} ({self.target_arch.estimated_params})\n\n"
            f"[dim]The expanded model inherits knowledge from the smaller model.[/dim]\n"
            f"[dim]Continue training to fully utilize the larger capacity.[/dim]\n\n"
            f"[yellow]Next:[/yellow] Run pre-training on the expanded model to continue learning!",
            title="🎉 Success",
            border_style="green"
        ))
        
        return str(output_path)
    
    def _interpolate_weights(self, source: torch.Tensor, target_shape: tuple) -> torch.Tensor:
        """
        Interpolate source weights to match target shape.
        Uses bilinear interpolation for 2D and trilinear for higher dims.
        """
        import torch.nn.functional as F
        
        # For 1D tensors (biases, layernorm)
        if len(source.shape) == 1:
            source_expanded = source.unsqueeze(0).unsqueeze(0)  # [1, 1, N]
            target = F.interpolate(source_expanded, size=target_shape[0], mode='linear', align_corners=True)
            return target.squeeze(0).squeeze(0)
        
        # For 2D tensors (linear layers, embeddings)
        elif len(source.shape) == 2:
            source_expanded = source.unsqueeze(0).unsqueeze(0)  # [1, 1, H, W]
            target = F.interpolate(source_expanded, size=target_shape, mode='bilinear', align_corners=True)
            return target.squeeze(0).squeeze(0)
        
        # For higher dims, just return random init
        else:
            return torch.randn(target_shape) * 0.02
    
    @staticmethod
    def get_expansion_path(current_arch: str) -> List[str]:
        """
        Get the recommended expansion path from current architecture.
        Returns list of architecture names from current to largest.
        """
        arch_order = list(ARCHITECTURES.keys())
        
        if current_arch not in arch_order:
            return arch_order
        
        current_idx = arch_order.index(current_arch)
        return arch_order[current_idx + 1:]


# ============================================================================
# Utility Functions
# ============================================================================

def list_architectures():
    """Display available model architectures."""
    table = Table(title="🏗️ Available Model Architectures", show_header=True, header_style="bold magenta")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Name", style="green")
    table.add_column("Parameters", width=10)
    table.add_column("VRAM", width=8)
    table.add_column("Description", width=50)
    
    for i, (key, arch) in enumerate(ARCHITECTURES.items(), 1):
        table.add_row(
            str(i),
            arch.display_name,
            arch.estimated_params,
            f"{arch.min_vram_gb}GB+",
            arch.description
        )
    
    console.print(table)


def list_pretrained_models(models_dir: str = "models") -> List[Dict[str, Any]]:
    """List all pre-trained models."""
    models = []
    models_path = Path(models_dir)
    
    if not models_path.exists():
        return models
        
    for model_dir in models_path.iterdir():
        if model_dir.is_dir():
            # Check for pre-trained model indicator
            final_path = model_dir / "final"
            config_path = final_path / "saara_config.json" if final_path.exists() else model_dir / "saara_config.json"
            
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config = json.load(f)
                    models.append({
                        "name": config.get("name", model_dir.name),
                        "path": str(final_path if final_path.exists() else model_dir),
                        "architecture": config.get("architecture", "unknown"),
                        "params": config.get("config", {}).get("estimated_params", "?"),
                    })
                except:
                    pass
                    
    return models


if __name__ == "__main__":
    # Test
    list_architectures()
