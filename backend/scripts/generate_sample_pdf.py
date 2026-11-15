import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "STUDY MATE AI - CS302: Generative AI & Machine Learning", border=0, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", border=0, align="C")

def create_sample_study_guide(output_path: str):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- PAGE 1: Course Overview & Supervised Learning ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(24, 76, 172)
    pdf.cell(0, 10, "Unit 1: Machine Learning Foundations", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "1.1 Taxonomy of Machine Learning", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    text1 = (
        "Machine Learning is categorized into three primary paradigms:\n\n"
        "1. Supervised Learning: Algorithms are trained using labeled datasets where each input feature vector "
        "X is paired with a ground truth target label Y. Key tasks include classification (predicting discrete class labels) "
        "and regression (predicting continuous numerical quantities). Popular algorithms include Logistic Regression, "
        "Support Vector Machines (SVM), and Random Forests.\n\n"
        "2. Unsupervised Learning: The algorithm is provided unlabeled data and must discover inherent structure, "
        "patterns, or cluster groupings without supervisor signals. Examples include K-Means clustering, Principal "
        "Component Analysis (PCA) for dimensionality reduction, and autoencoders.\n\n"
        "3. Reinforcement Learning: An autonomous agent learns to make sequences of decisions by taking actions in an "
        "environment to maximize cumulative rewards, balancing exploration and exploitation via Markov Decision Processes (MDP)."
    )
    pdf.multi_cell(0, 6, text1)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "1.2 Bias-Variance Tradeoff", ln=True)
    pdf.set_font("Helvetica", "", 10)
    text2 = (
        "High bias leads to underfitting: the model makes oversimplified assumptions and misses real trends in data.\n"
        "High variance leads to overfitting: the model memorizes training noise and fails to generalize to unseen test data.\n"
        "The optimal model minimizes total error = Bias^2 + Variance + Irreducible Noise."
    )
    pdf.multi_cell(0, 6, text2)

    # --- PAGE 2: Neural Networks & Transformer Architecture ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(24, 76, 172)
    pdf.cell(0, 10, "Unit 2: Deep Learning & Transformers", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "2.1 Activation Functions", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    text3 = (
        "Neural networks require non-linear activation functions to learn complex non-linear decision boundaries:\n\n"
        "- Rectified Linear Unit (ReLU): f(x) = max(0, x). It prevents vanishing gradient during backpropagation and is computationally efficient.\n"
        "- Sigmoid: f(x) = 1 / (1 + e^-x). Maps real numbers to range (0, 1), often used in binary classification output layers.\n"
        "- Softmax: Generalizes sigmoid to multi-class classification, generating probability distributions that sum to 1.0."
    )
    pdf.multi_cell(0, 6, text3)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "2.2 The Transformer & Scaled Dot-Product Attention", ln=True)
    pdf.set_font("Helvetica", "", 10)
    text4 = (
        "Introduced in 'Attention Is All You Need' (Vaswani et al., 2017), the Transformer architecture completely replaces "
        "recurrent layers with multi-head self-attention mechanisms.\n\n"
        "Each input token embedding is projected into three distinct learned vectors:\n"
        "1. Query vector (Q)\n"
        "2. Key vector (K)\n"
        "3. Value vector (V)\n\n"
        "The scaled dot-product attention formula is mathematically defined as:\n"
        "Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V\n\n"
        "Dividing by sqrt(d_k) prevents large dot products from pushing the softmax function into regions with extremely small gradients."
    )
    pdf.multi_cell(0, 6, text4)

    # --- PAGE 3: Retrieval-Augmented Generation (RAG) Architecture ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(24, 76, 172)
    pdf.cell(0, 10, "Unit 3: Retrieval-Augmented Generation (RAG)", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "3.1 Why RAG is Essential for Generative AI", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    text5 = (
        "Large Language Models (LLMs) suffer from two significant limitations:\n"
        "1. Hallucination: Generating plausible-sounding but factually fabricated responses.\n"
        "2. Knowledge Staleness: Training data cut-off prevents models from knowing proprietary notes or recent facts.\n\n"
        "RAG solves this by decoupling knowledge retrieval from knowledge generation. When a user asks a question, "
        "the system first queries an external indexed vector database (such as FAISS) to retrieve top-k semantically "
        "similar chunks, and injects those retrieved text excerpts into the LLM context prompt."
    )
    pdf.multi_cell(0, 6, text5)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "3.2 Vector Search with FAISS & Dense Embeddings", ln=True)
    pdf.set_font("Helvetica", "", 10)
    text6 = (
        "FAISS (Facebook AI Similarity Search) is an open-source library optimized for lightning-fast similarity search "
        "and clustering of high-dimensional vectors on CPUs and GPUs.\n\n"
        "Sentence Transformers (e.g., all-MiniLM-L6-v2) convert arbitrary text passages into 384-dimensional dense vectors "
        "such that semantically related concepts occupy nearby geometric positions in vector space, measured using Euclidean "
        "L2 distance or Cosine Similarity."
    )
    pdf.multi_cell(0, 6, text6)

    # Output file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"Sample PDF created at: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sample_notes")
    out_file = os.path.join(out_dir, "AI_and_Machine_Learning_Study_Notes.pdf")
    create_sample_study_guide(out_file)

