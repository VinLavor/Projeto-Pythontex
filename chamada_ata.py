import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from tkinter.ttk import Style
import os
from pyuca import Collator # importação pra lidar com os acentos nos nomes

class Chamada(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chamada para Ata")
        self.geometry("500x560")
        self.configure(bg="#4976AB")
        self.nomes = []
        self.caixas_marcadas = []
        self.criar_widgets()

    def criar_widgets(self):
        style = Style(self)
        style.configure("TFrame", background="#4976AB")
        style.configure("TCheckbutton", background="#4976AB", foreground="white")
        

        # frame do cabeçalho onde ficam os botões
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.place(x=0, y=0, relwidth=1, height=60)

        # label para colocar nossa belíssima logo
        self.image_label = ttk.Label(header_frame, background="#4976AB")

        # criação do frame dos botões
        button_frame = ttk.Frame(header_frame)
        button_frame.place(relx=1, rely=0, anchor='ne')  # Posiciona no canto superior direito

        # configurações para os botões
        style.configure(
            "RoundedButton.TButton",
            background="white",
            foreground="#4976AB",
            borderwidth=2,
            relief=tk.FLAT,
            padding=(10, 5),
        )

        load_button = ttk.Button(
            button_frame,
            text="Carregar Membros",
            command=self.carrega_nomes,
            style="RoundedButton.TButton",
        )
        load_button.pack(side=tk.LEFT, padx=5)

        save_button = ttk.Button(
            button_frame,
            text="Salvar Chamada",
            style="RoundedButton.TButton",
            command=self.salvar_chamada,
        )
        save_button.pack(side=tk.LEFT, padx=5)

        # frame de lista para nossa lista de nomes
        list_frame = ttk.Frame(self, style="TFrame")
        list_frame.place(x=10, y=70, relwidth=1, relheight=0.9)

        # Criação da barra de rolagem
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')  # Relaciona com o Canvas

        # configuração da barra de rolagem
        self.canvas = tk.Canvas(list_frame, yscrollcommand=scrollbar.set, bg="#4976AB")
        self.canvas.place(x=0, y=0, relwidth=0.95, relheight=1)

        # Conecta a barra de rolagem ao Canvas
        scrollbar.config(command=self.canvas.yview)

        # Um último frame para colocar os nomes dos membros
        self.inner_frame = ttk.Frame(self.canvas, style="TFrame")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor=tk.NW)

        # Configurar a região de rolagem do Canvas
        self.inner_frame.bind("<Configure>", self.atualizar_scrollregion)

        # Facilitar a rolagem com as teclas de seta
        self.canvas.bind_all("<Down>", lambda event: self.canvas.yview_scroll(1, "units"))
        self.canvas.bind_all("<Up>", lambda event: self.canvas.yview_scroll(-1, "units"))

    # Atualiza a região de rolagem do Canvas para se ajustar ao conteúdo
    def atualizar_scrollregion(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def carrega_logo(self, image_path):
        if not os.path.isfile(image_path):
            messagebox.showerror("Erro", "Arquivo de imagem não encontrado.")
            return

        try:
            imagem_original = Image.open(image_path)
            imagem_redimensionada = imagem_original.resize(
                (50, 50), Image.Resampling.LANCZOS
            )

            tk_image = ImageTk.PhotoImage(imagem_redimensionada)

            self.image_label.configure(image=tk_image)
            self.image_label.image = tk_image  # Mantém uma referência para evitar erro

            # posiciona a logo no canto superior esquerdo
            self.image_label.place(x=5, y=5, anchor='nw')  # Canto superior esquerdo

        except Exception as e:
            messagebox.showerror("Erro ao carregar a imagem", f"{e}")

    def carrega_nomes(self):
        caminho_do_arquivo = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not caminho_do_arquivo:
            return

        try:
            with open(caminho_do_arquivo, "r", encoding="utf-8") as f:
                self.nomes = [line.strip() for line in f if line.strip()]

            # Limpar o conteúdo existente antes de adicionar a nova lista de nomes
            for widget in self.inner_frame.winfo_children():
                widget.destroy()

            self.caixas_marcadas = []

            for nome in self.nomes:
                var = tk.BooleanVar()  # Para cada nome na lista, cria uma checkbox
                checkbox = ttk.Checkbutton(
                    self.inner_frame,
                    text=nome,
                    variable=var,
                    style="TCheckbutton",
                )
                checkbox.pack(anchor=tk.W, padx=10, pady=5)
                self.caixas_marcadas.append(var)

            # Atualiza a região de rolagem para se ajustar ao conteúdo
            self.canvas.update_idletasks()
            self.atualizar_scrollregion(None)

        except Exception as e:
            messagebox.showerror("Erro ao ler o arquivo", f"{e}")

    def salvar_chamada(self):
        if not self.nomes:
            messagebox.showwarning("Aviso", "Não há nomes para salvar.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                presentes = []
                ausentes = []
                # se a caixa está marcada adiciona normal, caso contrário, adiciona com textcolor
                for nome, var in zip(self.nomes, self.caixas_marcadas):
                    if var.get():
                        presentes.append(nome)
                    else:
                        ausentes.append(f"\\textcolor{{gray}}{{{nome}}}")

                todos_os_nomes = presentes + ausentes
                acentuador = Collator()

                def extrair_nome(nome):
                    if nome.startswith("\\textcolor{gray}"):
                        return nome.split("{")[2].split("}")[0]
                    return nome
                

                todos_os_nomes = sorted(todos_os_nomes, key=lambda nome: acentuador.sort_key(extrair_nome(nome)))

                nomes_organizados = ", ".join(todos_os_nomes)
                f.write(nomes_organizados + "\n")

            messagebox.showinfo("Sucesso", "Chamada salva com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro ao salvar a chamada", f"{e}")

if __name__ == "__main__":
    app = Chamada()
    image_path = "CARCARÁ.png"
    app.carrega_logo(image_path)
    app.mainloop()