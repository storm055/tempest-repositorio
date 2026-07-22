# MPT - Gerenciador de Pacotes para LFS (mpt)

Este repositório contém o projeto `mpt`, um gerenciador de pacotes minimalista para distros Linux baseadas em código-fonte.

## Estrutura

- `mpt/`: código do gerenciador de pacotes
- `packages/`: metadados e definições de pacotes
- `rootfs/`: sistema de arquivos de destino onde os pacotes são instalados
- `.mpt/`: dados internos do repositório (`index.json`, `installed.json`)

## Como usar

Inicialize o repositório:

```bash
python3 -m mpt.main init
```

Adicione um manifest de pacote:

```bash
python3 -m mpt.main add packages/hello.json
```

Instale um pacote:

```bash
python3 -m mpt.main install hello
```

Liste os pacotes disponíveis:

```bash
python3 -m mpt.main list
```

Liste os pacotes instalados:

```bash
python3 -m mpt.main list --installed
```

Remova um pacote:

```bash
python3 -m mpt.main remove hello
```

Verifique os arquivos de um pacote instalado:

```bash
python3 -m mpt.main verify hello
```
