import unittest
import os
import tempfile
from app import app, init_db, get_db

class PayrollTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a temporary database before each test."""
        # Create a temporary file to use as the database
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['DATABASE'] = self.db_path
        
        # Initialize the client and the database
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def tearDown(self):
        """Close and remove the temporary database after each test."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    # --- Helper Methods ---

    def add_employee(self, name, salary):
        """Helper to send a POST request to add an employee."""
        return self.client.post('/employees/add', data=dict(
            name=name,
            salary=salary
        ), follow_redirects=True)

    # --- Tests for Path: / (List Employees) ---

    def test_index_empty(self):
        """Test that the index page loads and shows no employees initially."""
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Employee List', rv.data)
        self.assertIn(b'No employees found', rv.data)

    def test_index_with_data(self):
        """Test that the index page lists employees after addition."""
        self.add_employee('Alice', '50000')
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Alice', rv.data)
        self.assertIn(b'50000.00', rv.data)

    # --- Tests for Path: /employees/add (Create) ---

    def test_add_employee_valid(self):
        """Test adding a valid employee (OAS 302 Response)."""
        rv = self.add_employee('Bob', '£35,000.50')
        self.assertEqual(rv.status_code, 200) # Follows redirect to index
        self.assertIn(b'Bob', rv.data)
        # 35000.50 * 100 = 3500050 pence -> formatted back to 35000.50
        self.assertIn(b'35000.50', rv.data) 

    def test_add_employee_invalid(self):
        """Test validation failure (OAS 400 Response)."""
        # Missing salary
        rv = self.add_employee('Charlie', '') 
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'Invalid input', rv.data)
        
        # Invalid salary format
        rv = self.add_employee('Charlie', 'Not a number')
        self.assertEqual(rv.status_code, 400)

    # --- Tests for Path: /employees/{id} (View) ---

    def test_view_employee(self):
        """Test viewing a specific employee detail page."""
        self.add_employee('David', '40000')
        
        # Assuming first ID is 1
        rv = self.client.get('/employees/1')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'David', rv.data)
        self.assertIn(b'40000.00', rv.data)

    def test_view_employee_not_found(self):
        """Test viewing a non-existent employee (OAS 404 Response)."""
        rv = self.client.get('/employees/999')
        self.assertEqual(rv.status_code, 404)

    # --- Tests for Path: /employees/{id}/edit (Update) ---

    def test_edit_employee_get(self):
        """Test loading the edit form."""
        self.add_employee('Eve', '60000')
        rv = self.client.get('/employees/1/edit')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Edit Employee', rv.data)
        self.assertIn(b'Eve', rv.data) # Value in input field

    def test_edit_employee_post(self):
        """Test submitting the edit form (OAS 302 Response)."""
        self.add_employee('Frank', '20000')
        
        rv = self.client.post('/employees/1/edit', data=dict(
            name='FrankUpdated',
            salary='25000'
        ), follow_redirects=True)
        
        self.assertEqual(rv.status_code, 200) # Redirects to detail view
        self.assertIn(b'FrankUpdated', rv.data)
        self.assertIn(b'25000.00', rv.data)

    def test_edit_employee_not_found(self):
        """Test editing a non-existent employee."""
        rv = self.client.post('/employees/999/edit', data=dict(
            name='Ghost',
            salary='0'
        ))
        self.assertEqual(rv.status_code, 404)

    # --- Tests for Path: /employees/{id}/delete (Delete) ---

    def test_delete_employee(self):
        """Test deleting an employee (OAS 302 Response)."""
        self.add_employee('Grace', '70000')
        
        # Verify she exists
        rv = self.client.get('/')
        self.assertIn(b'Grace', rv.data)
        
        # Delete
        rv = self.client.post('/employees/1/delete', follow_redirects=True)
        self.assertEqual(rv.status_code, 200) # Redirects to index
        
        # Verify she is gone
        self.assertNotIn(b'Grace', rv.data)

    def test_delete_employee_not_found(self):
        """Test deleting a non-existent employee."""
        rv = self.client.post('/employees/999/delete')
        self.assertEqual(rv.status_code, 404)

if __name__ == '__main__':
    unittest.main