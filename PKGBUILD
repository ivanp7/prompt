# Maintainer : Ivan Podmazov <ivanpzv [eight] at gmail com>

pkgname=prompt-ivanp7
pkgdesc="Simple and informative portable prompt"

pkgver=1
pkgrel=1

arch=('any')
license=('Unlicense')
depends=(python)

source=('prompt.py' 'prompt.sh')
md5sums=('4ec5b35efbbb425ad1957fdf0f36c2f4' '2c9895deca3b893a7617c6038b5a5bf3')

package ()
{
    install -Dm 755 prompt.py "$pkgdir/usr/bin/prompt.py"
    install -Dm 755 prompt.sh "$pkgdir/usr/bin/prompt.sh"
}

