import os

def imprimir_arbol(ruta_inicio):
    print(f"\n📂 ESTRUCTURA DEL PROYECTO: {os.path.abspath(ruta_inicio)}")
    print("="*50)
    
    # Carpetas que queremos ignorar para que no ensucien la vista
    ignorar = {'.git', '.venv', 'venv', '__pycache__', '.streamlit', '.vscode'}

    for root, dirs, files in os.walk(ruta_inicio):
        # Filtrar carpetas ignoradas
        dirs[:] = [d for d in dirs if d not in ignorar]
        
        level = root.replace(ruta_inicio, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}📁 {os.path.basename(root)}/')
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{subindent}📄 {f}')

if __name__ == "__main__":
    # Imprime la estructura desde la carpeta actual
    imprimir_arbol('.')
    print("="*50)