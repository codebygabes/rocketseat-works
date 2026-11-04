# Daily Diet API (Flask)

API REST para controle de dieta diária, feita com Flask e SQLAlchemy (SQLite).
Permite registrar refeições com nome, descrição, data/hora e se está dentro da dieta.

## Como rodar

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

A API sobe em `http://127.0.0.1:5000` e o banco `daily_diet.db` é criado automaticamente.

## Rotas

| Método | Rota             | Descrição                         |
|--------|------------------|-----------------------------------|
| POST   | `/meals`         | Cadastra uma refeição             |
| GET    | `/meals`         | Lista todas as refeições          |
| GET    | `/meals/<id>`    | Busca uma refeição                |
| PUT    | `/meals/<id>`    | Atualiza uma refeição             |
| DELETE | `/meals/<id>`    | Remove uma refeição               |
| GET    | `/meals/metrics` | Métricas e melhor sequência       |

### Exemplo de corpo (POST/PUT)

```json
{
  "name": "Salada",
  "description": "Salada com frango grelhado",
  "date_time": "2026-11-04T12:30:00",
  "is_on_diet": true
}
```

No PUT, todos os campos são opcionais.

## Testes

```bash
pip install pytest
pytest
```
