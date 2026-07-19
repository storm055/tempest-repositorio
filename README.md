# MPT - Gerenciador de Pacotes para LFS (mpt) 🚀

Este é um gerenciador de pacotes minimalista e baseado em código-fonte (Source-Based), desenvolvido em Bash para automação, compilação e manutenção do sistema **Linux From Scratch (LFS)**.

O objetivo do **mpt** é rastrear de forma limpa cada arquivo instalado via `make install` utilizando a variável de ambiente `DESTDIR`. Isso permite instalar, listar e remover programas do seu LFS com segurança, sem deixar arquivos órfãos espalhados pelo sistema.

---

