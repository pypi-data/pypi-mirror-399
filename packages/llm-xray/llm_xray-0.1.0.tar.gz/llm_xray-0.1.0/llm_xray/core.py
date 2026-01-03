import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelEngine:
    def __init__(self, model_name="gpt2"):
        self.tokenizer = None
        self.model = None
        self.model_name = model_name
        self.history = []  # Training history log
        
        # --- Device Optimization ---
        self.device = torch.device("cpu")
        try:
            import torch_directml
            if torch_directml.is_available():
                self.device = torch_directml.device()
                print("Hardware Acceleration: Using Intel Arc GPU (DirectML)")
            elif torch.cuda.is_available():
                self.device = torch.device("cuda")
                print("Hardware Acceleration: Using NVIDIA GPU (CUDA)")
        except ImportError:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                print("Hardware Acceleration: Using NVIDIA GPU (CUDA)")
            else:
                print("Using CPU (No hardware acceleration plugin found)")
        
    def load_model(self):
        print(f"Loading model {self.model_name}...")
        try:
            # Clear memory if possible (simple attempt)
            self.model = None
            self.tokenizer = None
            import gc
            gc.collect()
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
            print(f"Model loaded on {self.device}.")
        except Exception as e:
            print(f"FAILED to load model: {e}")
            print("Running in MOCK mode. Real model inference will not be available.")
            self.model = None
            self.tokenizer = None

    def set_model(self, model_name):
        self.model_name = model_name
        self.load_model()
        return self.model is not None



    def train(self, text, steps=10, learning_rate=5e-4):
        if not self.model or not self.tokenizer:
            return {"status": "error", "message": "Model not loaded"}

        self.model.train() # Set to training mode
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        # Tokenize and move to device
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        # For Causal LM, labels are the same as input_ids
        inputs['labels'] = inputs['input_ids'].clone()
        
        loss_history = []
        
        print(f"Training on text: '{text[:50]}...' for {steps} steps.")
        
        for i in range(steps):
            optimizer.zero_grad()
            outputs = self.model(**inputs)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            loss_history.append(loss.item())
            if i % 2 == 0:
                print(f"Step {i}: Loss {loss.item()}")

        self.model.eval() # Set back to eval mode
        
        # Log to history
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.history.append({
            "text": text[:30] + "..." if len(text) > 30 else text,
            "loss": round(loss_history[-1], 4),
            "steps": steps,
            "timestamp": timestamp
        })
        
        return {"status": "success", "final_loss": loss_history[-1], "steps": steps}

    def analyze(self, text, temperature=1.0):
        if not self.model and not self.tokenizer:
            # Try loading again if it was never attempted or failed previously? 
            if self.model_name:
                 self.load_model()
        
        if self.model is None:
            return {
                "tokens": ["(Mock)", "The", " sky", " is"],
                "top_k": [None, None, [{"token": "blue", "prob": 0.9}], [{"token": "blue", "prob": 0.5}]],
                "next_token_prediction": [{"token": "blue", "prob": 0.8}, {"token": "gray", "prob": 0.1}]
            }
        
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits # Shape: (batch_size, seq_len, vocab_size)
            
            # Apply temperature scaling
            # Avoid division by zero
            if temperature <= 0.01:
                temperature = 0.01
            
            logits = logits / temperature

        # we are interested in the probabilities for the *next* token prediction
        # The model predicts the next token at each position.
        # e.g. input: "The" -> predicts "sky" (logits[0, 0, :])
        
        # We want to see what the model thought about each token it saw/predicted.
        # Actually, standard causal LM training:
        # P(token_i | token_0...token_{i-1}) is logits[0, i-1, :]
        
        # Let's return the probabilities for the tokens that ARE in the text, 
        # plus the top-k alternatives for those positions.
        
        tokens = self.tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
        token_ids = inputs.input_ids[0].tolist()
        
        result_tokens = []
        result_top_k = []
        
        # For the first token, we don't have a previous context to predict it from (unless we assume BOS)
        # But usually we chart from the 2nd token onwards, or we just show the distribution for the *next* token.
        # User request "analyze this prompt". 
        # Let's show:
        # 1. The input tokens.
        # 2. For each input token (starting from 2nd), what was the prob of that token given context?
        # 3. What were the other top options?
        
        probabilities = torch.softmax(logits, dim=-1)
        
        # We align: prediction at index `i` corresponds to what the model thinks should come at `i+1`.
        # So logits[0, i] is the distribution for token at inputs.input_ids[0, i+1]
        
        # First token: No prediction (it's the start)
        result_tokens.append(tokens[0])
        result_top_k.append(None) # No context for first token
        
        for i in range(len(token_ids) - 1):
            current_token = tokens[i+1]
            # Prediction from previous position
            token_probs = probabilities[0, i, :] 
            
            # Get top k
            top_k = 5
            top_probs, top_indices = torch.topk(token_probs, top_k)
            
            top_k_data = []
            for prob, idx in zip(top_probs, top_indices):
                top_k_data.append({
                    "token": self.tokenizer.decode([idx]),
                    "prob": float(prob)
                })
            
            result_tokens.append(current_token)
            result_top_k.append(top_k_data)

        # Also predict the VERY NEXT token after the prompt ends (what it would generate next)
        next_token_probs = probabilities[0, -1, :]
        top_probs, top_indices = torch.topk(next_token_probs, 5)
        next_top_k_data = []
        for prob, idx in zip(top_probs, top_indices):
            next_top_k_data.append({
                "token": self.tokenizer.decode([idx]),
                "prob": float(prob)
            })
            
        return {
            "tokens": result_tokens,
            "top_k": result_top_k,
            "next_token_prediction": next_top_k_data
        }
