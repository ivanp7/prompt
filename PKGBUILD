# Maintainer : Ivan Podmazov <ivanpzv [eight] at gmail com>

pkgname=prompt-ivanp7
pkgdesc="Simple and informative portable prompt"

pkgver=1
pkgrel=1

arch=('any')
license=('Unlicense')
depends=(python)

source=('prompt.py')
md5sums=('47671b1776897e8e27a79f45cc91c01f')

package ()
{
    install -Dm 755 prompt.py "$pkgdir/usr/bin/prompt.py"
}

