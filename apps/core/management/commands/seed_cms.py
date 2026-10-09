"""
Idempotent CMS seed command for Nakashara Institutional CMS.
Supports:
  python manage.py seed_cms --demo
  python manage.py seed_cms --legal
  python manage.py seed_cms --navigation
"""

import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.models import Page, Site

from apps.content.models import (
    AnnouncementIndexPage,
    AnnouncementPage,
    ContactFormField,
    ContactPage,
    NoticeIndexPage,
    NoticePage,
    StandardPage,
)
from apps.departments.models import DepartmentIndexPage, DepartmentPage
from apps.documents.models import (
    CareerIndexPage,
    CareerPage,
    DocumentIndexPage,
    PublicationIndexPage,
    ReportIndexPage,
    TenderIndexPage,
    TenderPage,
)
from apps.events.models import EventIndexPage, EventPage
from apps.home.models import HomePage, QuickLinkItem
from apps.legal.models import LegalIndexPage, LegalPage
from apps.news.models import NewsCategory, NewsIndexPage, NewsPage
from apps.people.models import PersonCategory, PersonIndexPage, PersonPage
from apps.research.models import ResearchArea, ResearchIndexPage, ResearchProjectPage
from apps.site_settings.models import (
    FooterLink,
    FooterLinkGroup,
    NavMenuItem,
    SiteSettings,
)


class Command(BaseCommand):
    help = "Seed CMS with idempotent demonstration, legal, and navigation content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--demo", action="store_true", help="Seed full institutional demo site"
        )
        parser.add_argument(
            "--legal",
            action="store_true",
            help="Seed legal & policy placeholder pages only",
        )
        parser.add_argument(
            "--navigation", action="store_true", help="Seed navigation menus only"
        )

    def handle(self, *args, **options):
        run_all = not (options["demo"] or options["legal"] or options["navigation"])
        seed_demo = options["demo"] or run_all
        seed_legal = options["legal"] or run_all
        seed_nav = options["navigation"] or run_all

        root_page = Page.get_first_root_node()
        if not root_page:
            self.stdout.write(
                self.style.ERROR("No root page found. Run migrations first.")
            )
            return

        # Ensure HomePage exists as root's child or default site home
        home_page = HomePage.objects.first()
        if not home_page:
            # Check if default welcome page exists
            default_page = Page.objects.filter(slug="home").first()
            if default_page and not isinstance(default_page.specific, HomePage):
                default_page.delete()

            home_page = HomePage(
                title="Nakashara",
                slug="home",
                hero_headline="Pioneering Interdisciplinary Research & High-Impact Scholarship",
                hero_subheadline="An institutional sanctuary dedicated to rigorous scientific discovery, public interest technologies, and transformative learning.",
                hero_cta_label="Explore Research Centers",
                hero_cta_url="",
                intro="Nakashara is a premier public research and learning institution.",
            )
            root_page.add_child(instance=home_page)
            home_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Created HomePage."))
        else:
            self.stdout.write("HomePage already exists.")

        # Ensure Site points to HomePage
        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.root_page = home_page
            site.site_name = "Nakashara"
            site.save()
        else:
            Site.objects.create(
                hostname="localhost",
                port=8000,
                root_page=home_page,
                is_default_site=True,
                site_name="Nakashara",
            )

        # Configure SiteSettings
        site_settings = SiteSettings.for_site(Site.objects.get(is_default_site=True))
        site_settings.institution_name = "Nakashara"
        site_settings.institution_short_name = "NKSR"
        site_settings.tagline = "Advancing Knowledge, Technology, and Public Good"
        site_settings.footer_description = "Dedicated to the advancement of science, technology, public knowledge, and high-impact scholarship."
        site_settings.building_or_campus = "Administrative Complex, Block A"
        site_settings.address_line_1 = "Institutional Enclave, Campus Road"
        site_settings.address_line_2 = "Sector 4, Innovation District"
        site_settings.city = "Knowledge City"
        site_settings.state = "Karnataka"
        site_settings.postal_code = "560001"
        site_settings.country = "India"
        site_settings.email_general = "inquiry@nakashara.example.org"
        site_settings.email_admissions = "admissions@nakashara.example.org"
        site_settings.email_media = "media@nakashara.example.org"
        site_settings.email_reception = "reception@nakashara.example.org"
        site_settings.email_accessibility = "accessibility@nakashara.example.org"
        site_settings.phone_primary = "+91 80 2345 6789"
        site_settings.phone_secondary = "+91 80 2345 6790"
        site_settings.phone_toll_free = "1800 123 4567"
        site_settings.fax_number = "+91 80 2345 6799"
        site_settings.office_hours = "Monday – Friday: 08:30 AM – 05:30 PM IST"
        site_settings.directions_info = "Located adjacent to Knowledge Park Metro Station (Gate 2)."
        site_settings.directions_url = "https://maps.google.com"
        site_settings.footer_copyright_text = "Recognized by UGC and Ministry of Education."
        site_settings.twitter_url = "https://twitter.com/nakashara"
        site_settings.linkedin_url = "https://linkedin.com/company/nakashara"
        site_settings.youtube_url = "https://youtube.com/@nakashara"
        site_settings.save()

        # Seed Legal Pages
        if seed_legal:
            self.stdout.write("Seeding legal & policy placeholder pages...")
            legal_index = LegalIndexPage.objects.first()
            if not legal_index:
                legal_index = LegalIndexPage(
                    title="Policies & Legal",
                    slug="policies",
                    intro="<p>Official repository of Nakashara institutional policies, statutory disclosures, and compliance guidelines.</p>",
                )
                home_page.add_child(instance=legal_index)
                legal_index.save_revision().publish()

            # Seed placeholder policies
            policies_data = [
                {
                    "title": "Privacy Policy",
                    "slug": "privacy-policy",
                    "type": LegalPage.PolicyType.PRIVACY,
                    "summary": "<p>[DEMONSTRATION PLACEHOLDER] This policy governs data handling, website visitor privacy, and institutional record protection at Nakashara.</p>",
                },
                {
                    "title": "Accessibility Statement",
                    "slug": "accessibility-statement",
                    "type": LegalPage.PolicyType.ACCESSIBILITY,
                    "summary": "<p>[DEMONSTRATION PLACEHOLDER] Nakashara is committed to digital accessibility targeting WCAG 2.2 Level AA compliance.</p>",
                },
                {
                    "title": "Copyright & Fair Use",
                    "slug": "copyright-notice",
                    "type": LegalPage.PolicyType.COPYRIGHT,
                    "summary": "<p>[DEMONSTRATION PLACEHOLDER] Intellectual property, open-access publication guidelines, and institutional asset copyright statement.</p>",
                },
                {
                    "title": "Institutional Disclaimer",
                    "slug": "disclaimer",
                    "type": LegalPage.PolicyType.DISCLAIMER,
                    "summary": "<p>[DEMONSTRATION PLACEHOLDER] Standard informational disclaimer regarding external links, academic research, and published materials.</p>",
                },
                {
                    "title": "Terms of Website Use",
                    "slug": "terms-of-use",
                    "type": LegalPage.PolicyType.TERMS,
                    "summary": "<p>[DEMONSTRATION PLACEHOLDER] Acceptable usage policies for institutional network resources, public portals, and scholarly repositories.</p>",
                },
            ]

            today = timezone.now().date()
            for pol in policies_data:
                if not LegalPage.objects.filter(slug=pol["slug"]).exists():
                    p = LegalPage(
                        title=pol["title"],
                        slug=pol["slug"],
                        policy_type=pol["type"],
                        version="1.0-draft",
                        approval_status=LegalPage.ApprovalStatus.PUBLISHED,
                        approving_authority="Institutional Oversight Committee (Demo)",
                        approval_reference="NKSR/GOV/2026/POL-01",
                        approval_date=today,
                        effective_from=today,
                        last_reviewed_at=today,
                        next_review_at=today + datetime.timedelta(days=365),
                        owner_department="Office of Institutional Governance",
                        summary=pol["summary"],
                        contact_email="governance@nakashara.example.org",
                    )
                    legal_index.add_child(instance=p)
                    p.save_revision().publish()
                    self.stdout.write(f"  Created policy: {pol['title']}")

        # Seed Demo Content
        if seed_demo:
            self.stdout.write("Seeding demo institutional content...")

            # 1. Standard Pages: About, Leadership, Academics
            about_page = StandardPage.objects.filter(slug="about").first()
            if not about_page:
                about_page = StandardPage(
                    title="About Nakashara",
                    slug="about",
                    intro="<p>Established as an autonomous center of excellence, Nakashara integrates scientific inquiry with humanistic perspective.</p>",
                )
                home_page.add_child(instance=about_page)
                about_page.save_revision().publish()

            # 2. Departments
            dept_index = DepartmentIndexPage.objects.first()
            if not dept_index:
                dept_index = DepartmentIndexPage(
                    title="Departments & Centers",
                    slug="departments",
                    intro="<p>Discover our specialized academic departments, computational laboratories, and interdisciplinary centers.</p>",
                )
                home_page.add_child(instance=dept_index)
                dept_index.save_revision().publish()

            sample_depts = [
                (
                    "Department of Computational Sciences",
                    "CS",
                    "Pioneering foundations in scalable distributed computing, machine learning, and algorithmic fairness.",
                ),
                (
                    "Center for Molecular Bioengineering",
                    "CMB",
                    "Advancing molecular biophysics, computational genomics, and biomedical innovation.",
                ),
                (
                    "School of Public Policy and Governance",
                    "SPPG",
                    "Analyzing governance architectures, digital public infrastructure, and institutional economics.",
                ),
            ]
            for name, short, desc in sample_depts:
                s = short.lower()
                if not DepartmentPage.objects.filter(short_name=short).exists():
                    dp = DepartmentPage(
                        title=name,
                        slug=f"dept-{s}",
                        short_name=short,
                        description=f"<p>{desc}</p>",
                        contact_email=f"{s}@nakashara.example.org",
                        location="Academic Block A, Campus Main",
                    )
                    dept_index.add_child(instance=dp)
                    dp.save_revision().publish()
                    self.stdout.write(f"  Created department: {name}")

            # 3. News
            news_index = NewsIndexPage.objects.first()
            if not news_index:
                news_index = NewsIndexPage(
                    title="News & Press",
                    slug="news",
                    intro="<p>Institutional milestones, major research publications, and scholarly announcements.</p>",
                )
                home_page.add_child(instance=news_index)
                news_index.save_revision().publish()

            cat_research, _ = NewsCategory.objects.get_or_create(
                name="Research", slug="research"
            )
            cat_academic, _ = NewsCategory.objects.get_or_create(
                name="Campus", slug="campus"
            )

            if not NewsPage.objects.filter(
                slug="nakashara-inaugurates-quantum-lab"
            ).exists():
                np1 = NewsPage(
                    title="Nakashara Inaugurates High-Performance Computational Facility",
                    slug="nakashara-inaugurates-quantum-lab",
                    headline="Nakashara Commissioned New 10-Petaflop Research Computing Cluster",
                    summary="The multi-million research infrastructure will support molecular dynamics simulation and AI safety research.",
                    author_name="Office of Communications",
                    publication_date=timezone.now().date(),
                )
                news_index.add_child(instance=np1)
                np1.categories.add(cat_research)
                np1.save_revision().publish()

            # 4. Events
            event_index = EventIndexPage.objects.first()
            if not event_index:
                event_index = EventIndexPage(
                    title="Conferences & Events",
                    slug="events",
                    intro="<p>Colloquia, academic symposia, research workshops, and public lectures.</p>",
                )
                home_page.add_child(instance=event_index)
                event_index.save_revision().publish()

            if not EventPage.objects.filter(
                slug="annual-research-colloquium-2026"
            ).exists():
                ep1 = EventPage(
                    title="Annual Nakashara Research Colloquium 2026",
                    slug="annual-research-colloquium-2026",
                    summary="A two-day gathering of scholars presenting breakthroughs in computational and biological systems.",
                    start_datetime=timezone.now() + datetime.timedelta(days=14),
                    end_datetime=timezone.now() + datetime.timedelta(days=16),
                    location_name="Auditorium Hall 1, Main Campus",
                    registration_url="https://nakashara.example.org/register",
                )
                event_index.add_child(instance=ep1)
                ep1.save_revision().publish()

            # 5. Documents & Tenders
            doc_index = DocumentIndexPage.objects.first()
            if not doc_index:
                doc_index = DocumentIndexPage(
                    title="Documents & Downloads",
                    slug="documents",
                    intro="<p>Official institutional records, gazettes, guidelines, and forms.</p>",
                )
                home_page.add_child(instance=doc_index)
                doc_index.save_revision().publish()

            tender_index = TenderIndexPage.objects.first()
            if not tender_index:
                tender_index = TenderIndexPage(
                    title="Tenders & Procurement",
                    slug="tenders",
                )
                home_page.add_child(instance=tender_index)
                tender_index.save_revision().publish()

            if not TenderPage.objects.filter(
                slug="tender-laboratory-equipment-2026"
            ).exists():
                tp1 = TenderPage(
                    title="Supply and Installation of Advanced Electron Microscopy System",
                    slug="tender-laboratory-equipment-2026",
                    reference_number="NKSR/PROC/2026/042",
                    tender_type="goods",
                    status="open",
                    opening_date=timezone.now().date(),
                    closing_date=timezone.now().date() + datetime.timedelta(days=30),
                    estimated_value="Competitive Quotation",
                    description="<p>Sealed tenders are invited from authorized global manufacturers for the supply of high-resolution cryo-electron microscopy instrumentation.</p>",
                )
                tender_index.add_child(instance=tp1)
                tp1.save_revision().publish()

            # 6. Careers
            career_index = CareerIndexPage.objects.first()
            if not career_index:
                career_index = CareerIndexPage(
                    title="Careers",
                    slug="careers",
                )
                home_page.add_child(instance=career_index)
                career_index.save_revision().publish()

            if not CareerPage.objects.filter(
                slug="assistant-professor-computer-science"
            ).exists():
                cp1 = CareerPage(
                    title="Tenure-Track Assistant Professor in Computer Science",
                    slug="assistant-professor-computer-science",
                    position_type="faculty",
                    department="Department of Computational Sciences",
                    status="open",
                    closing_date=timezone.now().date() + datetime.timedelta(days=45),
                    description="<p>Applications are invited from outstanding researchers with expertise in distributed systems, security, or foundational AI.</p>",
                    qualifications="<p>Ph.D. in Computer Science or related discipline with evidence of high-impact scholarship.</p>",
                    application_email="recruitment@nakashara.example.org",
                )
                career_index.add_child(instance=cp1)
                cp1.save_revision().publish()

            # 7. Announcements & Notices
            ann_index = AnnouncementIndexPage.objects.first()
            if not ann_index:
                ann_index = AnnouncementIndexPage(
                    title="Announcements",
                    slug="announcements",
                    intro="<p>Latest institutional updates and advisories.</p>",
                )
                home_page.add_child(instance=ann_index)
                ann_index.save_revision().publish()

            if not AnnouncementPage.objects.filter(
                slug="autumn-semester-commencement"
            ).exists():
                ap1 = AnnouncementPage(
                    title="Commencement of Academic Semester 2026–27",
                    slug="autumn-semester-commencement",
                    summary="All faculty, researchers, and scholars are advised that the autumn academic session commences according to the published calendar.",
                    is_pinned=True,
                )
                ann_index.add_child(instance=ap1)
                ap1.save_revision().publish()

            not_index = NoticeIndexPage.objects.first()
            if not not_index:
                not_index = NoticeIndexPage(
                    title="Official Notices",
                    slug="notices",
                    intro="<p>Formal circulars, regulatory notifications, and administrative orders.</p>",
                )
                home_page.add_child(instance=not_index)
                not_index.save_revision().publish()

            if not NoticePage.objects.filter(
                slug="administrative-circular-campus-safety"
            ).exists():
                nop1 = NoticePage(
                    title="Institutional Policy Notification on Campus Environmental Safety Protocols",
                    slug="administrative-circular-campus-safety",
                    notice_number="REG/NOT/2026/012",
                    notice_date=timezone.now().date(),
                    issuing_authority="Office of the Registrar",
                    summary="Updated laboratory safety standards and environmental management guidelines applicable to all research facilities.",
                )
                not_index.add_child(instance=nop1)
                nop1.save_revision().publish()

            # 8. Research
            res_index = ResearchIndexPage.objects.first()
            if not res_index:
                res_index = ResearchIndexPage(
                    title="Research",
                    slug="research",
                    intro="<p>Strategic research initiatives and grant-funded investigation programs.</p>",
                )
                home_page.add_child(instance=res_index)
                res_index.save_revision().publish()

            area_ai, _ = ResearchArea.objects.get_or_create(
                name="Artificial Intelligence & Systems", slug="ai-systems"
            )
            if not ResearchProjectPage.objects.filter(
                slug="trustworthy-autonomous-systems"
            ).exists():
                rp1 = ResearchProjectPage(
                    title="Verification and Safety in Autonomous Robotic Systems",
                    slug="trustworthy-autonomous-systems",
                    summary="Developing formal verification techniques for safety-critical autonomous architectures operating under sensor uncertainty.",
                    principal_investigator="Prof. K. Ramanathan",
                    status="ongoing",
                    start_date=timezone.now().date() - datetime.timedelta(days=180),
                    funding_agency="National Science Foundation (Demo Grant)",
                    funding_amount="INR 1.2 Crore",
                )
                res_index.add_child(instance=rp1)
                rp1.areas.add(area_ai)
                rp1.save_revision().publish()

            # 9. People
            peo_index = PersonIndexPage.objects.first()
            if not peo_index:
                peo_index = PersonIndexPage(
                    title="People",
                    slug="people",
                    intro="<p>Scholars, research scientists, and administrative leadership of Nakashara.</p>",
                )
                home_page.add_child(instance=peo_index)
                peo_index.save_revision().publish()

            pcat_fac, _ = PersonCategory.objects.get_or_create(
                name="Faculty", slug="faculty"
            )
            cs_dept = DepartmentPage.objects.filter(short_name="CS").first()
            if not PersonPage.objects.filter(slug="prof-k-ramanathan").exists():
                pp1 = PersonPage(
                    title="Prof. K. Ramanathan",
                    slug="prof-k-ramanathan",
                    first_name="K.",
                    last_name="Ramanathan",
                    designation="Professor & Head of Computing",
                    department=cs_dept,
                    is_public_contact=True,
                    email="ramanathan@nakashara.example.org",
                    office_location="Computing Complex, Room 302",
                )
                peo_index.add_child(instance=pp1)
                pp1.categories.add(pcat_fac)
                pp1.save_revision().publish()

            # 10. Reports & Publications
            pub_index = PublicationIndexPage.objects.first()
            if not pub_index:
                pub_index = PublicationIndexPage(
                    title="Publications",
                    slug="publications",
                    intro="<p>Scholarly articles, books, and conference proceedings published by Nakashara faculty.</p>",
                )
                home_page.add_child(instance=pub_index)
                pub_index.save_revision().publish()

            rep_index = ReportIndexPage.objects.first()
            if not rep_index:
                rep_index = ReportIndexPage(
                    title="Annual Reports",
                    slug="reports",
                )
                home_page.add_child(instance=rep_index)
                rep_index.save_revision().publish()

            # 11. Contact Page
            contact_page = ContactPage.objects.first()
            if not contact_page:
                contact_page = ContactPage(
                    title="Contact Us",
                    slug="contact",
                    intro="<p>Have questions, inquiries, or feedback? Get in touch with our institutional offices or administrative teams.</p>",
                    thank_you_text="<p>Thank you for contacting Nakashara. Your inquiry has been received and our office will follow up shortly.</p>",
                    address_block="<p><strong>Nakashara Central Administration</strong></p><p>Administrative Block, Knowledge Park</p><p>Knowledge City, India — 560001</p>",
                    phone_primary="+91 80 2345 6789",
                    phone_secondary="+91 80 2345 6790",
                    email_contact="contact@nakashara.example.org",
                    from_address="noreply@nakashara.example.org",
                    to_address="inquiries@nakashara.example.org",
                    subject="Inquiry via Nakashara Contact Form",
                )
                home_page.add_child(instance=contact_page)
                ContactFormField.objects.create(
                    page=contact_page,
                    label="Full Name",
                    field_type="singleline",
                    required=True,
                    sort_order=0,
                )
                ContactFormField.objects.create(
                    page=contact_page,
                    label="Email Address",
                    field_type="email",
                    required=True,
                    sort_order=1,
                )
                ContactFormField.objects.create(
                    page=contact_page,
                    label="Subject / Department",
                    field_type="singleline",
                    required=False,
                    sort_order=2,
                )
                ContactFormField.objects.create(
                    page=contact_page,
                    label="Message",
                    field_type="multiline",
                    required=True,
                    sort_order=3,
                )
                contact_page.save_revision().publish()
                self.stdout.write("  Created contact page.")

        # Seed Navigation
        if seed_nav:
            self.stdout.write("Configuring navigation menus...")
            # Query existing index pages for internal linking
            dept_idx = DepartmentIndexPage.objects.first()
            res_idx = ResearchIndexPage.objects.first()
            peo_idx = PersonIndexPage.objects.first()
            news_idx = NewsIndexPage.objects.first()
            event_idx = EventIndexPage.objects.first()
            ann_idx = AnnouncementIndexPage.objects.first()
            not_idx = NoticeIndexPage.objects.first()
            doc_idx = DocumentIndexPage.objects.first()
            pub_idx = PublicationIndexPage.objects.first()
            rep_idx = ReportIndexPage.objects.first()
            ten_idx = TenderIndexPage.objects.first()
            car_idx = CareerIndexPage.objects.first()
            leg_idx = LegalIndexPage.objects.first()
            cnt_idx = ContactPage.objects.first()

            # Setup QuickLinkItems on HomePage using link_page for all models
            QuickLinkItem.objects.filter(page=home_page).delete()
            quick_links_def = [
                (
                    "Departments",
                    dept_idx,
                    "building-2",
                    "Academic and research departments",
                ),
                (
                    "Research",
                    res_idx,
                    "flask-conical",
                    "Pioneering projects and discovery",
                ),
                (
                    "Faculty & Staff",
                    peo_idx,
                    "users",
                    "Scholars, fellows, and leadership",
                ),
                (
                    "News & Media",
                    news_idx,
                    "newspaper",
                    "Press releases and announcements",
                ),
                ("Events", event_idx, "calendar", "Conferences, workshops, lectures"),
                (
                    "Official Notices",
                    not_idx,
                    "bell",
                    "Institutional circulars and orders",
                ),
                ("Announcements", ann_idx, "megaphone", "Campus updates and deadlines"),
                ("Documents", doc_idx, "folder", "Official repository and archives"),
                (
                    "Publications",
                    pub_idx,
                    "book-open",
                    "Scholarly publications and monographs",
                ),
                (
                    "Annual Reports",
                    rep_idx,
                    "file-bar-chart",
                    "Audits, governance and reports",
                ),
                ("Tenders", ten_idx, "briefcase", "Procurement and open tenders"),
                (
                    "Careers",
                    car_idx,
                    "graduation-cap",
                    "Faculty and administrative openings",
                ),
                (
                    "Legal & Policies",
                    leg_idx,
                    "shield-check",
                    "Statutory compliance and policies",
                ),
                (
                    "Contact",
                    cnt_idx,
                    "mail",
                    "Get in touch with administrative offices",
                ),
            ]
            for label, page_obj, icon, desc in quick_links_def:
                if page_obj:
                    QuickLinkItem.objects.create(
                        page=home_page,
                        label=label,
                        link_page=page_obj,
                        icon_name=icon,
                        description=desc,
                    )

            # Main Nav Menu Items
            NavMenuItem.objects.all().delete()
            main_nav_defs = [
                ("Home", home_page, 0),
                ("Departments", dept_idx, 1),
                ("Research", res_idx, 2),
                ("People", peo_idx, 3),
                ("News", news_idx, 4),
                ("Events", event_idx, 5),
                ("Announcements", ann_idx, 6),
                ("Tenders", ten_idx, 7),
                ("Careers", car_idx, 8),
                ("Contact", cnt_idx, 9),
            ]
            for label, p_obj, ord_idx in main_nav_defs:
                if p_obj:
                    NavMenuItem.objects.create(
                        label=label, page=p_obj, order=ord_idx, is_visible=True
                    )

            # Footer Link Groups
            FooterLinkGroup.objects.all().delete()
            grp_inst = FooterLinkGroup.objects.create(title="Institution", order=0)
            for lbl, p_obj, ord_idx in [
                ("Departments", dept_idx, 0),
                ("Research", res_idx, 1),
                ("Faculty & Directory", peo_idx, 2),
                ("Publications", pub_idx, 3),
                ("Annual Reports", rep_idx, 4),
            ]:
                if p_obj:
                    FooterLink.objects.create(
                        group=grp_inst, label=lbl, page=p_obj, order=ord_idx
                    )

            grp_public = FooterLinkGroup.objects.create(title="Public Notices", order=1)
            for lbl, p_obj, ord_idx in [
                ("Announcements", ann_idx, 0),
                ("Official Notices", not_idx, 1),
                ("Tenders", ten_idx, 2),
                ("Careers", car_idx, 3),
                ("Events", event_idx, 4),
                ("News", news_idx, 5),
            ]:
                if p_obj:
                    FooterLink.objects.create(
                        group=grp_public, label=lbl, page=p_obj, order=ord_idx
                    )

            grp_legal = FooterLinkGroup.objects.create(
                title="Legal & Policies", order=2
            )
            if leg_idx:
                FooterLink.objects.create(
                    group=grp_legal,
                    label="Policies & Governance",
                    page=leg_idx,
                    order=0,
                )
            if cnt_idx:
                FooterLink.objects.create(
                    group=grp_legal, label="Contact & Grievances", page=cnt_idx, order=1
                )

        self.stdout.write(
            self.style.SUCCESS(
                "CMS seeding completed successfully. Safe to run repeatedly."
            )
        )
