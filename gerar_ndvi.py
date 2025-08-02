import customtkinter as ctk
import rasterio
import matplotlib.pyplot as plt
from tkinter import filedialog
import os
from PIL import Image
import tkinter.messagebox as msgbox

# Variáveis globais
red_path = None
nir_path = None
ndvi_final = None
profile = None

#FUNÇÕES

#Abre seletor de arquivo para escolher a banda RED (vermelha)
def buscar_red():
    global red_path
    caminho = filedialog.askopenfilename(filetypes=[("Arquivos TIFF", "*.tif *.tiff")])
    if caminho:
        if not caminho.lower().endswith(('.tif', '.tiff')):
            msgbox.showwarning("Aviso", "Por favor, selecione um arquivo TIFF (.tif ou .tiff).")
            return
        red_path = caminho
        nome = os.path.basename(caminho)
        if len(nome) > 30:
            nome = nome[:27] + "..."
        lbl_red.configure(text=f'Selecionado: {nome}')

# Abre seletor de arquivo para escolher a banda NIR (Infravermelha)
def buscar_nir():
    global nir_path
    caminho = filedialog.askopenfilename(filetypes=[("Arquivos TIFF", "*.tif *.tiff")])
    if caminho:
        if not caminho.lower().endswith(('.tif', '.tiff')):
            msgbox.showwarning("Aviso", "Por favor, selecione um arquivo TIFF (.tif ou .tiff).")
            return  # sai da função sem atualizar
        nir_path = caminho
        nome = os.path.basename(caminho)
        if len(nome) > 30:
            nome = nome[:27] + "..."
        lbl_nir.configure(text=f'Selecionado: {nome}')

# Calcula o índice NDVI com base nas bandas RED e NIR selecionadas
def calcular_ndvi():
    global ndvi_final, profile
    # Verifica se as duas bandas foram selecionadas antes de continuar
    if not red_path and not nir_path:
        msgbox.showwarning("Aviso", "Por favor, selecione as bandas RED e NIR para continuar.")
    elif not red_path:
        msgbox.showwarning("Aviso", "Por favor, selecione a banda RED.")
    elif not nir_path:
        msgbox.showwarning("Aviso", "Por favor, selecione a banda NIR")
    else:
        print("Calculando o NDVI")
        with rasterio.open(red_path) as red_src, rasterio.open(nir_path) as nir_src:
            red = red_src.read(1)
            nir = nir_src.read(1)
            ndvi_final = (nir.astype(float) - red.astype(float)) / (nir + red + 1e-6)
            profile = red_src.meta
        msgbox.showinfo("Aviso","NDVI Calculado com Sucesso!")
        plt.imshow(ndvi_final, cmap = "RdYlGn", vmin = -1, vmax = 1)
        plt.colorbar()
        plt.title("NDVI")
        plt.show()
    
# Mostra o NDVI calculado em um gráfico com colormap
def mostrar_ndvi():
    if ndvi_final is None:
        msgbox.showwarning("Aviso", "O NDVI ainda não foi calculado. Por favor, calcule antes de visualizar.")
    else:
        plt.imshow(ndvi_final, cmap = "RdYlGn", vmin = -1, vmax = 1)
        plt.colorbar()
        plt.title("NDVI")
        plt.show()

# Salva o resultado NDVI em formato GeoTIFF usando o perfil da banda RED
def salvar_ndvi():
    global ndvi_final, profile
    if ndvi_final is None or profile is None:
        msgbox.showwarning("Aviso", "O NDVI ainda não foi calculado. Por favor, calcule antes de salvar.")
        return
    
    # Atualiza o metadata para refletir tipo de dado e número de bandas
    profile.update(dtype = rasterio.float32, count = 1)

    nome_arquivo = filedialog.asksaveasfilename(
        defaultextension= '.tif',
        filetypes=[('GeoTIFF', '*tif;*.tiff')],
        title = 'Salvar NDVI como...'
    )
    if nome_arquivo:
        with rasterio.open(nome_arquivo, 'w', **profile) as dst:
            dst.write(ndvi_final.astype(rasterio.float32), 1)
        msgbox.showinfo("Aviso", f'NDVI salvo em: {nome_arquivo}')

# Janela principal
janela = ctk.CTk()
janela.geometry('600x600')
janela.title("NDVI")
janela.configure(fg_color="#F1F8E9")
#janela.resizable(False, False)

# Carrega e exibe a imagem de fundo como decoração da interface
imagem_fundo = Image.open("fundo.png")
imagem_fundo = imagem_fundo.resize((600, 600))  # redimensionar pra caber certinho

imagem_fundo_ctk = ctk.CTkImage(
    light_image=imagem_fundo,
    dark_image=imagem_fundo,
    size=(600, 600)
)

label_fundo = ctk.CTkLabel(janela, image=imagem_fundo_ctk, text="")
label_fundo.place(x=0, y=0, relwidth=1, relheight=1)

# Dicionário com estilo padronizado para os botões da interface
botao_estilo = {
    "font": ("Poppins", 16, "bold"),
    "fg_color": "#2E3756",
    "hover_color": "#2E7D63",
    "text_color": "#FFFFFF",  
    "corner_radius": 25,
    "width": 180,
    "height": 45,
    "border_width":2,
    "border_color": "#CECECE"
}

# Título
titulo = ctk.CTkFrame(janela, fg_color = "transparent")
titulo.pack(pady = 20)

lbl_titulo = ctk.CTkLabel(
    master=titulo,
    text=" Análise NDVI",
    text_color="#2E3756",
    fg_color = "transparent",
    font=("Poppins", 40, 'bold')
)
lbl_titulo.pack()

# Painel para selecionar banda RED
painel_red = ctk.CTkFrame(
    master=janela,
    width=400,
    height=60,
    fg_color='white',
    corner_radius=50
)
painel_red.pack(pady = 10)
painel_red.pack_propagate(False)

# Define layout em grade para alinhar texto e botão no painel
painel_red.grid_columnconfigure(0, weight=1)
painel_red.grid_columnconfigure(1, weight=0)
painel_red.grid_rowconfigure(0, weight=1)

lbl_red = ctk.CTkLabel(
    master=painel_red,
    text="Selecione a Banda Vermelha:",
    text_color="#4D4D4D",
    font=('Poppins', 14),
    anchor="w"
)
lbl_red.grid(row=0, column=0, sticky="ew", padx=(15, 10), pady=10)

botao_red = ctk.CTkButton(
    master=painel_red,
    text="Selecionar",
    command = buscar_red,
    **botao_estilo
)
botao_red.grid(row=0, column=1, padx=(0, 15), pady=10)

# Painel para selecionar banda NIR
painel_nir = ctk.CTkFrame(
    master=janela,
    width=400,
    height=60,
    fg_color='white',
    corner_radius=50
)
painel_nir.pack(pady = 10)
painel_nir.pack_propagate(False)

# Define layout em grade para alinhar texto e botão no painel
painel_nir.grid_columnconfigure(0, weight=1)
painel_nir.grid_columnconfigure(1, weight=0)
painel_nir.grid_rowconfigure(0, weight=1)

lbl_nir = ctk.CTkLabel(
    master=painel_nir,
    text="Selecione a Banda Infravermelha:",
    text_color="#4D4D4D",
    font=('Poppins', 14),
    anchor= "w"
)
lbl_nir.grid(row=0, column=0, sticky="ew", padx=(15, 10), pady=10)

botao_nir = ctk.CTkButton(
    master=painel_nir,
    text="Selecionar",
    command = buscar_nir,
    **botao_estilo
)
botao_nir.grid(row=0, column=1, padx=(0, 15), pady=10)

# Botão para calcular o NDVI
botao_calcular_ndvi = ctk.CTkButton(
    master=janela,
    text="Calcular NDVI",
    command = calcular_ndvi,
    **botao_estilo
)
botao_calcular_ndvi.pack(pady = 20)

# Botão para mostrar o NDVI
botao_mostrar_ndvi = ctk.CTkButton(
    master=janela,
    text="Mostrar NDVI",
    command = mostrar_ndvi,
    **botao_estilo
)
botao_mostrar_ndvi.pack(pady = 20)

# Botão para salvar o arquivo NDVI
botao_salvar_ndvi = ctk.CTkButton(
    master=janela,
    text="Salvar NDVI",
    command = salvar_ndvi,
    **botao_estilo,
)
botao_salvar_ndvi.pack(pady = 20)

# Loop principal da interface
janela.mainloop()