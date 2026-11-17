# Maintainer: GKPROEJECT
pkgname=avilon
pkgver=3.5
pkgrel=1
pkgdesc='Desktop game library for maps, guides, and resources'
arch=('any')
url='https://github.com/GKPROEJECT/Avilon'
license=('MIT')
depends=(
  'gst-plugins-good'
  'python'
  'python-gobject'
  'python-pillow'
  'python-pywebview'
  'tk'
  'webkit2gtk-4.1'
)
source=(
  'Avilon_clean.py'
  'LICENSE'
  'README.md'
  'avilon'
  'avilon.desktop'
  'logo.ico'
  'logo.png'
)
sha256sums=(
  '7840e7e23fd7cb724b1da4d9764e793016ae7a9f790d9482fe7b66a7d447f081'
  '3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986'
  '03520fe8d5e0b3d3739efd83efbaa67b5aeecb2196183bca635459d7529b1c62'
  '56ee0d262488f63f80dd14ee5fe67a92e0db28b70a8e73303ef18b6cdde4d926'
  '02f7fddbe5122b83e138357f6ca73ec10b621340f7411133f3f9b06c46477271'
  '2f0ae7b7e4c22e8c3ac31449f7ea10770b922995f7689b4e9c3c4d89de86e89f'
  'd77a0329e301e39762b84c5385c37ce9b0cc19cf9b92f3bb66ca33bba31c680e'
)

package() {
  install -Dm644 Avilon_clean.py "$pkgdir/usr/lib/avilon/Avilon_clean.py"
  install -Dm644 logo.png "$pkgdir/usr/lib/avilon/logo.png"
  install -Dm644 logo.ico "$pkgdir/usr/lib/avilon/logo.ico"
  install -Dm755 avilon "$pkgdir/usr/bin/avilon"
  install -Dm644 avilon.desktop "$pkgdir/usr/share/applications/avilon.desktop"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
  install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
  install -d "$pkgdir/usr/share/pixmaps"
  python - "$pkgdir/usr/share/pixmaps/avilon.png" <<'PY'
from PIL import Image
import sys

with Image.open("logo.ico") as source:
    source.convert("RGBA").save(sys.argv[1], format="PNG")
PY
}
