# Diagrama de Secuencia

## Comment · Add

```mermaid
sequenceDiagram
    actor User
    participant Application
    participant Database
    User -> Application: Enviar quote y comentario
    Application -> Application: Validar comentario
    alt Comentario no válido
        Application -> User: Informar de error
        Application -> User: Redirigir a página previa
    end
    Application -> Application: Almacenar tiempo actual
    Application -> Application: Crear objeto Comment
    Application -> Database: Almacenar Comment
    Application -> User: Informar de éxito
    Application -> User: Redirigir a página previa
```
