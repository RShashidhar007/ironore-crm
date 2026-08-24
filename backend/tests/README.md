# Backend Tests

This directory contains test scripts for the Iron Ore CRM backend features.

## Test Scripts

### 1. `test_quotation_flow.py`
Tests the complete quotation workflow end-to-end.

**What it tests:**
- User login
- Request for quotation (product list retrieval)
- Product selection and quotation submission
- Quotation generation with PDF
- Price calculation from historical data

**How to run:**
```bash
python tests/test_quotation_flow.py
```

**Expected output:**
```
✓ Login successful
✓ Product list retrieved (5 products)
✓ Quotation generated successfully
✓ PDF created
✓ Pricing calculated correctly
```

**Requirements:**
- Backend server running on http://localhost:8000
- Database populated with products and inventory
- Test user credentials: user_id="shashi", password="test123"

---

### 2. `test_email_feature.py`
Tests the "Contact Company via Email" feature.

**What it tests:**
- User login
- Email retrieval from environment config
- Email display in response
- Mailto link generation

**How to run:**
```bash
python tests/test_email_feature.py
```

**Expected output:**
```
✓ Login successful
✓ Email retrieved: rshashidhar513@gmail.com
✓ Mailto link working: mailto:rshashidhar513@gmail.com
✓ TEST PASSED
```

**Requirements:**
- Backend server running on http://localhost:8000
- `.env` file with `COMPANY_SUPPORT_EMAIL` configured
- Test user credentials: user_id="shashi", password="test123"

---

## Running All Tests

```bash
cd backend
python tests/test_quotation_flow.py
python tests/test_email_feature.py
```

---

## Environment Setup

Before running tests, ensure:

1. **Backend is running:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Database is populated:**
   - Products in InventoryMaster
   - Inventory data available
   - User accounts created

3. **Test user exists:**
   - User ID: `shashi`
   - Password: `test123`
   - User Role: Customer or Admin

4. **Environment variables are set:**
   - `COMPANY_SUPPORT_EMAIL=rshashidhar513@gmail.com`
   - `OLLAMA_BASE_URL=http://localhost:11434`
   - Other database settings

---

## Adding New Tests

To add new tests:

1. Create a new file: `test_<feature_name>.py`
2. Follow the pattern from existing tests
3. Use descriptive test steps
4. Print clear success/failure messages
5. Update this README

---

## Troubleshooting

### "Connection refused" error
- Make sure backend is running on port 8000
- Check if uvicorn process is active

### "Invalid user ID or password"
- Verify test user exists in database
- Check password hash is correct
- Update test credentials if changed

### "No email in response"
- Ensure action is passed correctly: `"action": "Contact Company via Email"`
- Check .env file has `COMPANY_SUPPORT_EMAIL` set

### "No products available"
- Populate InventoryMaster with test products
- Run seed_data script first

---

## Test Architecture

Each test follows this pattern:

```python
1. Login
   ↓
2. Test specific feature
   ↓
3. Verify response
   ↓
4. Print results
```

This ensures tests are isolated and easy to debug.

---

**Last Updated:** August 22, 2026
