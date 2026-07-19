# MPT - Gerenciador de Pacotes para LFS (mpt) 🚀

Este é um gerenciador de pacotes minimalista e baseado em código-fonte (Source-Based), desenvolvido em Bash para automação, compilação e manutenção do sistema **Linux From Scratch (LFS)**.

O objetivo do **mpt** é rastrear de forma limpa cada arquivo instalado via `make install` utilizando a variável de ambiente `DESTDIR`. Isso permite instalar, listar e remover programas do seu LFS com segurança, sem deixar arquivos órfãos espalhados pelo sistema.

---

## 📁 Estrutura do Repositório

*   `mpt.sh`: Script principal que gerencia o download, extração, compilação, instalação e remoção dos pacotes.
*   `receitas/`: Diretório contendo os scripts de instruções (`.sh`) customizados para cada programa (ex: `bash.sh`, `wget.sh`).

---

## 🛠️ Como Instalar no LFS

No terminal do seu sistema LFS, clone este repositório privado na pasta `/opt` (lembre-se de usar seu Token de Acesso se o repositório for privado) e dê permissão de execução ao script principal:

```bash
cd /opt
sudo git clone https://github.com
cd mpt
sudo chmod +x mpt.sh
```

Para facilitar o uso e poder rodar o comando `mpt` de qualquer lugar do terminal, crie um link simbólico para ele:
```bash
sudo ln -sf /opt/mpt/mpt.sh /usr/local/bin/mpt
```

---

## 💻 Como Usar

Com o link simbólico criado, o gerenciador funciona através de argumentos simples diretamente no seu terminal:

### 1. Instalar um pacote (Compilar a partir da receita)
```bash
sudo mpt -i nome_do_pacote
```
*Exemplo:* `sudo mpt -i htop`

### 2. Listar pacotes instalados no sistema
```bash
mpt -l
```

### 3. Remover um pacote completamente
```bash
sudo mpt -r nome_do_pacote
```

---

## 📝 Como criar uma nova receita

Para adicionar um novo programa ao seu repositório, crie um arquivo `.sh` dentro da pasta `receitas/` seguindo o modelo estruturado abaixo:

```bash
# receitas/htop.sh
NOME="htop"
VERSAO="3.3.0"
URL="https://github.com"

compilar() {
    ./autogen.sh
    ./configure --prefix=/usr
    make
}

instalar() {
    make DESTDIR="\$DESTDIR" install
}
```

---

## ⚙️ Como funciona por trás dos panos?

1. **Download & Extração:** O script baixa o código-fonte compactado diretamente para `/var/cache/mpt` e o extrai de forma isolada dentro de `/tmp/mpt`.
2. **Build Seguro:** A compilação (`./configure` e `make`) ocorre normalmente. No entanto, o comando `make install` é redirecionado para um diretório temporário específico de staging usando a variável `DESTDIR`.
3. **Log de Rastreamento:** O **mpt** executa um escaneamento via `find` na pasta temporária, mapeia a árvore exata de arquivos gerados pelo software e salva esse índice de texto em `/var/log/mpt/nome_do_pacote.files`.
4. **Instalação e Remoção Limpa:** Os arquivos mapeados são copiados diretamente para o sistema real (`/`). Quando a remoção (`-r`) é solicitada, o **mpt** lê o arquivo de log e apaga cirurgicamente apenas os itens que pertencem àquele pacote, preservando a integridade do LFS.
