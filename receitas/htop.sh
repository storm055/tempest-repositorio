NOME="htop"
VERSAO="3.3.0"
URL="https://github.com"

compilar() {
    # El comando ./autogen.sh es necesario si compilas desde la rama de desarrollo de htop
    # Si da error en tu LFS por falta de herramientas, puedes comentarlo con un #
    ./autogen.sh
    ./configure --prefix=/usr
    make
}

instalar() {
    make DESTDIR="$DESTDIR" install
}

