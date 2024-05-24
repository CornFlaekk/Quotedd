# Diagrama de Secuencia

## Search

```mermaid
sequenceDiagram
    actor User
    participant Application
    participant Database
    User -> Application: Enviar cadena de búsqueda
    Application -> Database: Recuperar Quotes, QuoteLists, Comments y Users con la cadena de búsqueda
    Application -> Application: Elegir tipo con más resultados
    alt Ningún objeto encontrado
        Application -> User: Informar que no hay resultados
    else Se han encontrado resultados
    Application -> User: Redirigir a la vista donde haya más resultados
    end
```
