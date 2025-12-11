import csv
import os
import pickle
from typing import Dict, Any

TXT_FILE = "coleccion.txt"
BIN_FILE = "estadisticas.bin"
FIELDNAMES = ["id", "nombre", "categoria", "anio", "creador", "calificacion"]

def crear_archivo_txt_si_no_existe():
    if not os.path.exists(TXT_FILE):
        try:
            with open(TXT_FILE, "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter='|')
                writer.writeheader()
        except Exception as e:
            print(f"[ERROR] No se pudo crear {TXT_FILE}: {e}")
            raise

def guardar_elemento_txt(elemento: Dict[str, Any]):
    crear_archivo_txt_si_no_existe()
    try:
        if not elemento["nombre"].strip():
            raise ValueError("El nombre no puede estar vacío.")
        cal = float(elemento["calificacion"])
        if not (0 <= cal <= 10):
            raise ValueError("La calificación debe estar entre 0 y 10.")
    except ValueError:
        raise
    except Exception as e:
        raise
    try:
        with open(TXT_FILE, "a", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter='|')
            writer.writerow(elemento)
    except Exception as e:
        print(f"[ERROR] No se pudo escribir en {TXT_FILE}: {e}")
        raise

def leer_toda_coleccion() -> list:
    crear_archivo_txt_si_no_existe()
    items = []
    try:
        with open(TXT_FILE, "r", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=FIELDNAMES, delimiter='|')
            next(reader, None)
            for row in reader:
                items.append(row)
    except FileNotFoundError:
        raise
    except Exception as e:
        print(f"[ERROR] Leyendo {TXT_FILE}: {e}")
        raise
    return items

def buscar_por_nombre(nombre: str) -> list:
    nombre = nombre.strip().lower()
    resultados = []
    try:
        for item in leer_toda_coleccion():
            if nombre in item["nombre"].strip().lower():
                resultados.append(item)
    except Exception:
        raise
    return resultados

def leer_estadisticas_binarias() -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(BIN_FILE):
        return {}
    try:
        with open(BIN_FILE, "rb") as f:
            data = pickle.load(f)
            if not isinstance(data, dict):
                raise ValueError("Formato de datos binarios inesperado.")
            return data
    except (EOFError, pickle.UnpicklingError):
        print("[AVISO] El archivo binario está vacío o corrupto. Se creará uno nuevo al guardar.")
        return {}
    except Exception as e:
        print(f"[ERROR] Al leer {BIN_FILE}: {e}")
        raise

def escribir_estadisticas_binarias(data: Dict[str, Dict[str, Any]]):
    try:
        with open(BIN_FILE, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"[ERROR] Al escribir {BIN_FILE}: {e}")
        raise

def asociar_estadistica_a_id(id_: str, estad: Dict[str, Any]):
    if not id_.strip():
        raise ValueError("ID inválido para asociar estadística.")
    data = leer_estadisticas_binarias()
    try:
        rare = int(estad.get("rareza", 0))
        if not (1 <= rare <= 100):
            raise ValueError("Rareza debe estar entre 1 y 100.")
        estad["rareza"] = rare
        estad["poder"] = int(estad.get("poder", 0))
        estad["popularidad"] = int(estad.get("popularidad", 0))
        estad["vistas"] = int(estad.get("vistas", 0))
    except ValueError:
        raise
    data[id_] = estad
    escribir_estadisticas_binarias(data)

def generar_nuevo_id() -> str:
    items = leer_toda_coleccion()
    ids = []
    for it in items:
        try:
            ids.append(int(it["id"]))
        except Exception:
            pass
    nuevo = max(ids) + 1 if ids else 1
    return str(nuevo)

def mostrar_item(item: Dict[str, Any]):
    print(f"ID: {item['id']} | Nombre: {item['nombre']} | Categoría: {item['categoria']} | Año: {item['anio']} | Creador: {item['creador']} | Calificación: {item['calificacion']}")

def mostrar_estadisticas_por_id(id_: str):
    stats = leer_estadisticas_binarias()
    if id_ in stats:
        s = stats[id_]
        print(f"Estadísticas de ID {id_}: Poder={s.get('poder')} Popularidad={s.get('popularidad')} Vistas={s.get('vistas')} Rareza={s.get('rareza')}")
    else:
        print("No hay estadísticas asociadas a ese ID.")

def opcion_agregar_elemento():
    try:
        nuevo_id = generar_nuevo_id()
        nombre = input("Nombre: ").strip()
        categoria = input("Categoría: ").strip()
        anio = input("Año (ej. 2023): ").strip()
        creador = input("Creador: ").strip()
        calificacion = input("Calificación (0-10): ").strip()
        elemento = {
            "id": nuevo_id,
            "nombre": nombre,
            "categoria": categoria,
            "anio": anio,
            "creador": creador,
            "calificacion": calificacion
        }
        try:
            guardar_elemento_txt(elemento)
            print(f"[OK] Elemento '{nombre}' guardado con ID {nuevo_id}.")
        except ValueError as ve:
            print(f"[ERROR] Datos inválidos: {ve}")
            return
        print("Ahora añade las estadísticas (valores enteros). Si no quieres, deja vacío y se guardará 0.")
        try:
            poder = input("  Poder (int): ").strip() or "0"
            popularidad = input("  Popularidad (int): ").strip() or "0"
            vistas = input("  Vistas (int): ").strip() or "0"
            rareza = input("  Rareza (1-100): ").strip() or "0"
            estad = {"poder": int(poder), "popularidad": int(popularidad), "vistas": int(vistas), "rareza": int(rareza)}
            asociar_estadistica_a_id(nuevo_id, estad)
            print("[OK] Estadísticas asociadas correctamente.")
        except ValueError as ve:
            print(f"[ERROR] Estadísticas inválidas: {ve}. No se guardaron las estadísticas.")
    except Exception as e:
        print(f"[ERROR] Al agregar elemento: {e}")

def opcion_mostrar_coleccion():
    try:
        items = leer_toda_coleccion()
        if not items:
            print("Colección vacía.")
            return
        print("\n=== Lista completa ===")
        for it in items:
            mostrar_item(it)
    except Exception as e:
        print(f"[ERROR] {e}")

def opcion_buscar_por_nombre():
    nombre = input("Escribe el nombre (o parte) a buscar: ").strip()
    if not nombre:
        print("Entrada vacía.")
        return
    try:
        resultados = buscar_por_nombre(nombre)
        if not resultados:
            print("No se encontraron resultados.")
            return
        for r in resultados:
            mostrar_item(r)
            mostrar_estadisticas_por_id(r["id"])
    except Exception as e:
        print(f"[ERROR] {e}")

def opcion_mostrar_datos_binarios():
    try:
        stats = leer_estadisticas_binarias()
        if not stats:
            print("No hay datos binarios guardados.")
            return
        print("\n=== Estadísticas guardadas (por ID) ===")
        for id_, s in stats.items():
            print(f"ID {id_}: {s}")
    except Exception as e:
        print(f"[ERROR] {e}")

def pre_cargar_ejemplos():
    try:
        items = leer_toda_coleccion()
        if len(items) >= 5:
            return
    except Exception:
        pass
    ejemplos = [
        {"id": "1", "nombre": "PikaMon", "categoria": "Eléctrico", "anio": "1996", "creador": "Satoshi", "calificacion": "9.0"},
        {"id": "2", "nombre": "AquaDrake", "categoria": "Agua", "anio": "2001", "creador": "Marina", "calificacion": "8.5"},
        {"id": "3", "nombre": "TerraGolem", "categoria": "Tierra", "anio": "1999", "creador": "Gaia", "calificacion": "8.8"},
        {"id": "4", "nombre": "NeoFlame", "categoria": "Fuego", "anio": "2005", "creador": "Ignis", "calificacion": "9.2"},
        {"id": "5", "nombre": "WindSprite", "categoria": "Aire", "anio": "2010", "creador": "Zeph", "calificacion": "7.9"},
    ]
    try:
        crear_archivo_txt_si_no_existe()
        existing = leer_toda_coleccion()
        if existing:
            print("[AVISO] El archivo ya contiene datos; no se precargarán ejemplos.")
            return
        for e in ejemplos:
            guardar_elemento_txt(e)
        ejemplo_stats = {
            "1": {"poder": 85, "popularidad": 92, "vistas": 1200, "rareza": 15},
            "2": {"poder": 70, "popularidad": 80, "vistas": 800, "rareza": 25},
            "3": {"poder": 90, "popularidad": 75, "vistas": 650, "rareza": 40},
            "4": {"poder": 95, "popularidad": 88, "vistas": 1500, "rareza": 10},
            "5": {"poder": 60, "popularidad": 60, "vistas": 400, "rareza": 55},
        }
        escribir_estadisticas_binarias(ejemplo_stats)
        print("[OK] Se han precargado 5 ejemplos en la colección.")
    except Exception as e:
        print(f"[ERROR] Al precargar ejemplos: {e}")

def menu_principal():
    print("===== MINI POKEDEX =====")
    print("1. Agregar elemento")
    print("2. Mostrar colección completa")
    print("3. Buscar elemento por nombre")
    print("4. Mostrar datos binarios (estadísticas)")
    print("5. Salir")
    while True:
        try:
            opcion = input("\nSelecciona una opción (1-5): ").strip()
            if opcion == "1":
                opcion_agregar_elemento()
            elif opcion == "2":
                opcion_mostrar_coleccion()
            elif opcion == "3":
                opcion_buscar_por_nombre()
            elif opcion == "4":
                opcion_mostrar_datos_binarios()
            elif opcion == "5":
                print("Saliendo. ¡Hasta luego!")
                break
            else:
                print("Opción inválida. Intenta de nuevo.")
        except KeyboardInterrupt:
            print("\nInterrumpido por el usuario. Saliendo.")
            break
        except Exception as e:
            print(f"[ERROR GENERAL] {e}")
        finally:
            print("\n(Escribe 1-5 para elegir otra opción)")

if __name__ == "__main__":
    try:
        print("Iniciando MiniPokedex...")
        if not os.path.exists(TXT_FILE) or not os.path.exists(BIN_FILE):
            print("Archivos de datos no encontrados.")
            respuesta = input("¿Deseas precargar 5 ejemplos de muestra? (s/n): ").strip().lower()
            if respuesta == "s":
                pre_cargar_ejemplos()
            else:
                crear_archivo_txt_si_no_existe()
                if not os.path.exists(BIN_FILE):
                    escribir_estadisticas_binarias({})
        menu_principal()
    except Exception as e:
        print(f"[FATAL] Error en la inicialización: {e}")
    finally:
        print("Programa terminado.")