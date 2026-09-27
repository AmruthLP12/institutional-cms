import pytest

from apps.departments.models import DepartmentIndexPage, DepartmentPage


@pytest.mark.django_db
class TestDepartmentsApp:
    def test_department_listing_and_detail(self, client, home_page):
        dept_index = DepartmentIndexPage(title="Departments", slug="departments")
        home_page.add_child(instance=dept_index)
        dept_index.save_revision().publish()

        dept = DepartmentPage(
            title="Department of Biological Sciences",
            slug="bio-sci",
            short_name="BIO",
            description="<p>Cellular and molecular biology laboratory.</p>",
            contact_email="bio@nakashara.example.org",
            location="Science Quadrangle, Room 101",
        )
        dept_index.add_child(instance=dept)
        dept.save_revision().publish()

        # Listing test
        res_list = client.get("/departments/")
        assert res_list.status_code == 200
        assert "Department of Biological Sciences" in res_list.content.decode()

        # Detail test
        res_detail = client.get("/departments/bio-sci/")
        assert res_detail.status_code == 200
        content = res_detail.content.decode()
        assert "Department of Biological Sciences" in content
        assert "bio@nakashara.example.org" in content
