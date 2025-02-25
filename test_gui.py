import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import json
from datetime import datetime
from ai_review import scrape_vendor_documentation, extract_document_text, analyze_ai_capabilities, get_vendor_documentation

# Import your functions or define them here
# from ai_review import scrape_vendor_documentation, extract_document_text, analyze_ai_capabilities

class AIReviewTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Capability Review Tool - Testing Interface")
        self.root.geometry("900x700")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL input
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="Vendor URL:").pack(side=tk.LEFT, padx=5)
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.url_entry.insert(0, "https://www.microsoft.com")
        
        ttk.Button(url_frame, text="Scrape", command=self.run_scrape).pack(side=tk.LEFT, padx=5)
        
        # Notebook for different sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tab 1: Documentation URLs
        self.docs_frame = ttk.Frame(notebook)
        notebook.add(self.docs_frame, text="Documentation URLs")
        
        docs_scroll = ttk.Frame(self.docs_frame)
        docs_scroll.pack(fill=tk.BOTH, expand=True)
        
        self.docs_text = scrolledtext.ScrolledText(docs_scroll, wrap=tk.WORD)
        self.docs_text.pack(fill=tk.BOTH, expand=True)
        
        docs_btn_frame = ttk.Frame(self.docs_frame)
        docs_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(docs_btn_frame, text="Extract Content", 
                  command=self.run_extract).pack(side=tk.LEFT, padx=5)
        
        # Tab 2: Extracted Content
        self.content_frame = ttk.Frame(notebook)
        notebook.add(self.content_frame, text="Extracted Content")
        
        content_scroll = ttk.Frame(self.content_frame)
        content_scroll.pack(fill=tk.BOTH, expand=True)
        
        self.content_text = scrolledtext.ScrolledText(content_scroll, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        content_btn_frame = ttk.Frame(self.content_frame)
        content_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(content_btn_frame, text="Analyze", 
                  command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        
        # Tab 3: Analysis Results
        self.analysis_frame = ttk.Frame(notebook)
        notebook.add(self.analysis_frame, text="Analysis Results")
        
        analysis_scroll = ttk.Frame(self.analysis_frame)
        analysis_scroll.pack(fill=tk.BOTH, expand=True)
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_scroll, wrap=tk.WORD)
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        
        analysis_btn_frame = ttk.Frame(self.analysis_frame)
        analysis_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(analysis_btn_frame, text="Save Results", 
                  command=self.save_results).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(main_frame, textvariable=self.status_var, 
                 relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, pady=5)
        
        # Store data
        self.doc_urls = {}
        self.doc_texts = {}
        self.analysis_results = {}
    
    def run_scrape(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_var.set("Please enter a URL")
            return
        
        self.status_var.set(f"Scraping {url}...")
        self.docs_text.delete(1.0, tk.END)
        
        def scrape_thread():
            try:
                self.doc_urls = get_vendor_documentation(url)
                
                self.root.after(0, lambda: self.docs_text.insert(tk.END, 
                                                                json.dumps(self.doc_urls, indent=2)))
                self.root.after(0, lambda: self.status_var.set(
                    f"Found {sum(1 for v in self.doc_urls.values() if v)} document links"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.root.after(0, lambda: self.docs_text.insert(tk.END, f"Error: {str(e)}"))
        
        thread = threading.Thread(target=scrape_thread)
        thread.daemon = True
        thread.start()
    
    def run_extract(self):
        if not self.doc_urls:
            self.status_var.set("No documents to extract. Run scraping first.")
            return
        
        self.status_var.set("Extracting content...")
        self.content_text.delete(1.0, tk.END)
        
        def extract_thread():
            try:
                self.doc_texts = {}
                
                for doc_type, url in self.doc_urls.items():
                    if url:
                        self.root.after(0, lambda: self.status_var.set(f"Extracting {doc_type}..."))
                        try:
                            text = extract_document_text(url)
                            self.doc_texts[doc_type] = text
                        except Exception as e:
                            self.root.after(0, lambda: self.content_text.insert(
                                tk.END, f"Error extracting {doc_type}: {str(e)}\n\n"))
                
                summary = {doc_type: f"{len(text)} characters" 
                          for doc_type, text in self.doc_texts.items()}
                
                self.root.after(0, lambda: self.content_text.insert(
                    tk.END, f"Extracted content summary:\n{json.dumps(summary, indent=2)}\n\n"))
                
                for doc_type, text in self.doc_texts.items():
                    preview = text[:300] + "..." if len(text) > 300 else text
                    self.root.after(0, lambda: self.content_text.insert(
                        tk.END, f"\n--- {doc_type} preview ---\n{preview}\n"))
                
                self.root.after(0, lambda: self.status_var.set(
                    f"Extracted content from {len(self.doc_texts)} documents"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
        
        thread = threading.Thread(target=extract_thread)
        thread.daemon = True
        thread.start()
    
    def run_analysis(self):
        if not self.doc_texts:
            self.status_var.set("No content to analyze. Extract content first.")
            return
        
        self.status_var.set("Analyzing AI capabilities...")
        self.analysis_text.delete(1.0, tk.END)
        
        def analyze_thread():
            try:
                self.analysis_results = analyze_ai_capabilities(self.doc_texts)
                
                self.root.after(0, lambda: self.analysis_text.insert(
                    tk.END, json.dumps(self.analysis_results, indent=2)))
                
                self.root.after(0, lambda: self.status_var.set("Analysis complete"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.root.after(0, lambda: self.analysis_text.insert(tk.END, f"Error: {str(e)}"))
        
        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()
    
    def save_results(self):
        if not self.analysis_results:
            self.status_var.set("No analysis results to save.")
            return
        
        vendor = self.url_entry.get().split("//")[1].split(".")[1]
        filename = f"analysis_{vendor}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w") as f:
            json.dump({
                "vendor_url": self.url_entry.get(),
                "doc_urls": self.doc_urls,
                "analysis": self.analysis_results
            }, f, indent=2)
        
        self.status_var.set(f"Results saved to {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AIReviewTestGUI(root)
    root.mainloop()