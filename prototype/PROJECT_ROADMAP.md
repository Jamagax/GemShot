# 🚀 LifeOS Project Roadmap & Log

Este documento actúa como el "Cerebro Central" del desarrollo de LifeOS. Aquí se registran los Hitos (Milestones), Tareas Pendientes y el Historial de Cambios.

## 🏆 Hitos (Milestones)

### Fase 1: Génesis (Completado) ✅
- [x] Crear estructura base PARA.
- [x] Desarrollar script de captura de pantalla con `mss`.
- [x] Integrar `customtkinter` para GUI moderna.
- [x] Conectar con Gemini 1.5 Flash para análisis de imágenes.

### Fase 2: Refinamiento UIX (En Progreso) 🚧
- [x] Migrar diseño a "Light SaaS Style" (LifeOS Capture Station).
- [x] Implementar herramientas de dibujo (Lápiz, Rectángulo).
- [x] **Fix**: Flechas con puntas geométricas correctas (Pillow).
- [x] **Feat**: Herramienta de Texto funcional.
- [x] **Sys**: Sistema de Logging centralizado (`logger_agent`).

### Fase 3: Robustez y Distribución (En Progreso) 📅
- [x] **Refactorización de Código**: Separar `lifeos_capture_ultimate.py` en módulos (`ui.py`, `backend.py`, `config.py`) para mantenibilidad.
- [ ] **Configuración UI**: Crear panel de ajustes para cambiar API Keys y Rutas sin editar YAML.
- [x] **System Tray**: Minimizar la app a la bandeja del sistema (reloj) en lugar de cerrarla.
- [ ] **Instalador**: Generar `.exe` con PyInstaller para despliegue fácil.

## 📝 Backlog de Tareas (To-Do)

### Prioridad Alta
- [ ] **Setup API Gemini**: Detectar si falta la API Key y pedirla al usuario o tener un botón para configurarla.
- [ ] **Validación de Rutas**: Asegurar que si el drive no está conectado, la app no crashee y use una carpeta local temporal.
- [ ] **Feedback Visual AI**: Mostrar un indicador de carga más bonito (spinner) mientras Gemini piensa.
- [ ] **Historial Local**: Pequeña galería en la UI para ver las últimas 5 capturas.

### Prioridad Media
- [ ] **Temas Dinámicos**: Permitir cambiar entre "Cyber-Zen" (Oscuro) y "SaaS Light" (Claro).
- [ ] **Obsidian URI**: Botón para "Abrir en Obsidian" directamente tras guardar.

## 📜 Changelog (Registro Automático)
*(El agente de logs escribirá aquí los eventos importantes)*
- 2024-12-19: Inicio del sistema de logs y creación del Roadmap.
