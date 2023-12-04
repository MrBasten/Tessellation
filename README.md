# Автоматическая тесселяция stl геометрии
<p align="center"> Основные требования: 
</p>

<p align="center">
   <img src="https://img.shields.io/badge/python-3.10.11-blue" alt="Python Version">
   <img src="https://img.shields.io/badge/np-1.24.2-blue" alt="NumPy Version">
   <img src="https://img.shields.io/badge/pyvista-0.39.1-green" alt="Pyvista Version">
   <img src="https://img.shields.io/badge/pyacvd-0.2.9-green" alt="Pyacvd Version">
   <img src="https://img.shields.io/badge/blender->= 3.0-orange" alt="Blender Version">
</p>

Данный проект разработан в рамках МАИ. 

Этот проект использует алгоритм [ManidoldPlus](https://github.com/hjwdzh/ManifoldPlus)
## Цель проекта
В рамках проекта ведётся разработка модуля геометрического препроцессинга дискретных моделей (поверхностная сетка тел) для дальнейшего использования в задачах CFD.

## Инструкция и требования 
Команды для терминала:
```
cd путь\до\проекта
python main.py "-f" "-d"`
```

Аргументы при запуске: 
-f(--folder) - промежуточные папки; 
-d(--depth) - параметр ManifoldPlus глубина работы.

## Пример работы