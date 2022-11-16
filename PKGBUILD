# Maintainer : Ivan Podmazov <ivanpzv [eight] at gmail com>

pkgname=prompt-ivanp7
pkgdesc="Simple and informative portable prompt"

pkgver=1
pkgrel=1

arch=('any')
license=('Unlicense')
depends=(python)

source=('prompt.py')
md5sums=('19fab8ea593806a6ec070d7b561082f0')

package ()
{
    install -Dm 755 prompt.py "$pkgdir/usr/bin/prompt.py"
}

