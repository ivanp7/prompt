# Maintainer : Ivan Podmazov <ivanpzv [eight] at gmail com>

pkgname=prompt-ivanp7
pkgdesc="Simple and informative portable prompt"

pkgver=1
pkgrel=2

arch=('any')
license=('Unlicense')
depends=(python)

source=('prompt.py' 'prompt.sh')
sha256sums=('a23fac35ec520d95b5eec8cd147b28fc144df6c787fb828598c79cf5bed64c48'
            'b5540dd8db81d886309445488b4ab1c4a273e8eebce7913733a16a13d8f2cef9')

package ()
{
    install -Dm 755 prompt.py "$pkgdir/usr/bin/prompt.py"
    install -Dm 755 prompt.sh "$pkgdir/usr/bin/prompt.sh"
}

