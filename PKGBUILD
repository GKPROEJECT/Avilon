# Maintainer: GKPROEJECT
pkgname=avilon
pkgver=3.0
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
  '99830772a9a0a8176d8a87ffecb569bcae45a9f7663ce216df4d3282b68d2477'
  '712ad6b038cf616723ba50bb37022aef5095ce0356ba0cb73f1399b11c89649c'
  'f7c25c7eaf8f72dab72475e4a4c19d0d63cc6b6c656cfe2fcdccd7ce176fcbbd'
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
