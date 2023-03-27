# Maintainer : Ivan Podmazov <ivanpzv [eight] at gmail com>

pkgname=prompt-ivanp7
pkgdesc="Simple and informative portable prompt"

pkgver=1
pkgrel=2

arch=('any')
license=('Unlicense')
depends=(python)

source=('prompt.py' 'prompt.sh')
sha256sums=('fb3b5cfc3f4adb261f44e8e5643667bf7570668853deb9f575075305f84597c3'
            'de44ce45270698d78ebb60215e5cb0ab8d6801cc8b7059e483a090827d47859e')

package ()
{
    install -Dm 755 prompt.py "$pkgdir/usr/bin/prompt.py"
    install -Dm 755 prompt.sh "$pkgdir/usr/bin/prompt.sh"
}

