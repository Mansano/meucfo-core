#!/usr/bin/env python3
"""
Script de inicialização do MeuCFO.ai
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Verifica se todos os requisitos estão instalados"""
    required_files = [
        '.env',
        'requirements.txt',
        'app/main.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Arquivos faltando:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def setup_environment():
    """Configura ambiente se necessário"""
    env_file = Path('.env')
    if not env_file.exists():
        print("📝 Criando arquivo .env a partir do exemplo...")
        env_example = Path('.env.example')
        if env_example.exists():
            env_example.copy(env_file)
            print("✅ Arquivo .env criado. Por favor, configure as variáveis.")
            return False
        else:
            print("❌ Arquivo .env.example não encontrado!")
            return False
    
    return True

def run_docker():
    """Executa com Docker Compose"""
    print("🐳 Iniciando com Docker Compose...")
    try:
        subprocess.run(['docker-compose', 'up', '--build'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar Docker Compose: {e}")
        return False
    except FileNotFoundError:
        print("❌ Docker Compose não encontrado. Instale Docker.")
        return False
    
    return True

def run_local():
    """Executa localmente com Uvicorn"""
    print("🚀 Iniciando servidor local...")
    try:
        # Verificar se Redis está rodando
        import redis
        from app.config import settings
        
        try:
            r = redis.Redis.from_url(settings.REDIS_URL)
            r.ping()
            print("✅ Redis conectado")
        except:
            print("⚠️  Redis não está disponível. Rate limiting não funcionará.")
        
        # Iniciar servidor
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=settings.APP_PORT,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Dependências faltando: {e}")
        print("📦 Instale as dependências com: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("""
    ╔═══════════════════════════════════════════╗
    ║        MeuCFO.ai - Inicialização         ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Verificar arquivos necessários
    if not check_requirements():
        sys.exit(1)
    
    # Configurar ambiente
    if not setup_environment():
        sys.exit(1)
    
    # Menu de opções
    print("\n📋 Escolha o modo de execução:")
    print("1. 🐳 Docker Compose (Recomendado)")
    print("2. 🚀 Local com Uvicorn")
    print("3. 📦 Instalar dependências")
    print("4. 🧪 Executar testes")
    print("5. 🚪 Sair")
    
    choice = input("\n👉 Selecione uma opção (1-5): ").strip()
    
    if choice == '1':
        run_docker()
    elif choice == '2':
        run_local()
    elif choice == '3':
        print("📦 Instalando dependências...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependências instaladas.")
    elif choice == '4':
        print("🧪 Executando testes...")
        subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'])
    elif choice == '5':
        print("👋 Até mais!")
        sys.exit(0)
    else:
        print("❌ Opção inválida.")
        sys.exit(1)

if __name__ == '__main__':
    main()
