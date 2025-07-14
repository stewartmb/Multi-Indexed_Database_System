import cv2
import os
import sys

def load_and_verify_image(path):
    """Carga una imagen y verifica su integridad"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {path} (¿Formato inválido?)")
    
    if img.dtype != 'uint8':
        img = cv2.convertScaleAbs(img)
        print(f"Convertida imagen a uint8: {path}")
    
    return img

def main():
    try:
        # Configuración de rutas
        script_dir = os.path.dirname(os.path.abspath(__file__))
        test_images_dir = os.path.join(script_dir, 'test_images')
        
        # Verificar existencia del directorio
        if not os.path.exists(test_images_dir):
            raise FileNotFoundError(f"Directorio no encontrado: {test_images_dir}")

        # Rutas completas de imágenes
        img1_path = os.path.join(test_images_dir, 'Lionel_Messi_0001.jpg')
        img2_path = os.path.join(test_images_dir, 'Lionel_Messi_0002.jpg')

        # Cargar y verificar imágenes
        img1 = load_and_verify_image(img1_path)
        img2 = load_and_verify_image(img2_path)

        # Inicializar SIFT
        sift = cv2.SIFT_create()

        # Extraer características
        keypoints1, descriptors1 = sift.detectAndCompute(img1, None)
        keypoints2, descriptors2 = sift.detectAndCompute(img2, None)

        # Verificar descriptores
        if descriptors1 is None or descriptors2 is None:
            raise ValueError("No se pudieron extraer descriptores (¿imágenes muy uniformes?)")

        # Emparejar características
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
        matches = bf.match(descriptors1, descriptors2)

        # Mostrar resultados
        result = cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches, None)
        cv2.imshow('Resultado SIFT', result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        print("\n🔍 Posibles soluciones:")
        print("- Verifica que las imágenes existen en test_images/")
        print("- Asegúrate que son archivos JPG/PNG válidos")
        print("- Comprueba permisos de lectura en los archivos")
        print("- Prueba con imágenes más pequeñas o menos comprimidas")
        sys.exit(1)

if __name__ == "__main__":
    main()