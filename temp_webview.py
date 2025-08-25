
import sys
import os

try:
    import webview
    
    def main():
        webview.create_window(
            title="Mapa - sdffd",
            url="https://maps.tcno.co/gzw",
            width=1200,
            height=800,
            resizable=True,
            shadow=True,
            text_select=True
        )
        webview.start(debug=False)

    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"Error en webview: {e}")
    import webbrowser
    webbrowser.open("https://maps.tcno.co/gzw")
