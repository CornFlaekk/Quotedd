# Diagrama de Secuencia

## Login

```mermaid
sequenceDiagram
    actor User
    participant Application
    User -> Application: Enviar username y password
    Application -> Application: Validar datos
    alt Datos no válidos
        Application -> User: Informar del error
        Application -> User: Redirigir a /login
    else Datos válidos
        Application -> Application: Iniciar sesión
        Application -> User: Informar del éxito
        Application -> User: Redirigir a /home
    end
```
