import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.routing_service import determine_routing

client = TestClient(app)


def test_example_1_clean_enterprise_rfp():
    res = determine_routing(
        from_name="Suresh Kulkarni",
        from_email="s.kulkarni@meridiansteel.co.in",
        subject="RFP - Enterprise Document Management System",
        body="Meridian Steel invites proposals for an enterprise DMS covering 4 plants and ~1,200 users. Indicative budget is Rs. 25 lakhs. Proposals must reach us by 12th August 2026.",
        received_at="2026-08-01T09:14:22+05:30"
    )
    assert res["should_skip"] is False
    assert res["assignee_id"] == "u_aarti"
    assert res["category"] == "enterprise_rfp"
    assert res["priority"] == "medium"
    assert res["due_date"] == "2026-08-12"
    assert res["deal_value_inr"] == 2500000
    assert res["company_name"] == "Meridian Steel"


def test_example_2_smb_demo_request_no_value():
    res = determine_routing(
        from_name="Ankit Bose",
        from_email="ankit@railyardlogistics.in",
        subject="Quick demo request",
        body="Hi, we're a 30-person logistics startup in Pune... can we get a demo sometime next week? Nothing urgent. — Ankit Bose, Founder, Railyard Logistics",
        received_at="2026-08-01T11:02:10+05:30"
    )
    assert res["should_skip"] is False
    assert res["assignee_id"] == "u_rohit"
    assert res["category"] == "smb_enquiry"
    assert res["priority"] == "low"
    assert res["due_date"] is None
    assert res["deal_value_inr"] is None
    assert res["company_name"] == "Railyard Logistics"


def test_example_3_psu_tender_below_threshold():
    res = determine_routing(
        from_name="Procurement Officer",
        from_email="tender.desk@bhel.in",
        subject="Tender Notice No. BHEL/PROC/2026/0847",
        body="Tender Notice No. BHEL/PROC/2026/0847. Bharat Heavy Electricals Limited invites bids for supply of analytics software licences. Estimated value: Rs. 6,50,000. Last date for bid submission: 03-08-2026, 1700 hrs IST.",
        received_at="2026-08-01T14:20:00+05:30"
    )
    assert res["should_skip"] is False
    assert res["assignee_id"] == "u_aarti"
    assert res["category"] == "enterprise_rfp"
    assert res["priority"] == "high"  # ~51 hours away
    assert res["due_date"] == "2026-08-03"
    assert res["deal_value_inr"] == 650000
    assert "Bharat Heavy Electricals" in (res["company_name"] or "")


def test_example_4_marketing_sponsorship_hard_deadline():
    res = determine_routing(
        from_name="Nandita Reddy",
        from_email="nandita@saassummit.in",
        subject="Sponsorship confirmation needed",
        body="We're finalising sponsors for the India SaaS Summit in Bengaluru. Gold tier is ₹4,00,000 and includes a keynote slot. We need confirmation by tomorrow EOD as we're going to print. — Nandita Reddy, Sponsorship Lead",
        received_at="2026-08-02T16:45:00+05:30"
    )
    assert res["should_skip"] is False
    assert res["assignee_id"] == "u_meera"
    assert res["category"] == "marketing"
    assert res["priority"] == "high"
    assert res["due_date"] == "2026-08-03"
    assert res["deal_value_inr"] == 400000
    assert res["company_name"] == "India SaaS Summit"


def test_example_5_finance_invoice():
    res = determine_routing(
        from_name="Accounts Dept",
        from_email="billing@vantagecloud.com",
        subject="Overdue invoice INV-2026-0331",
        body="Please find attached invoice INV-2026-0331 for Rs. 1,18,000 (incl. 18% GST) against PO-88214. Kindly process — payment terms were Net 30 and this is now 12 days overdue. Also, our GSTIN has changed, updated details attached.",
        received_at="2026-08-03T10:30:00+05:30"
    )
    assert res["should_skip"] is False
    assert res["assignee_id"] == "u_divya"
    assert res["category"] == "finance"
    assert res["priority"] == "high"
    assert res["due_date"] is None
    assert res["deal_value_inr"] is None  # Must NOT set deal value for invoices!
    assert res["company_name"] == "Vantage Cloud Services"


def test_example_6_alliances():
    res = determine_routing(
        from_name="Tariq Mansoor",
        from_email="tariq@zenithcloudpartners.com",
        subject="Partner Collaboration & Reselling Opportunity",
        body="We're a Salesforce implementation partner across MEA with 40+ enterprise clients. We'd like to explore reselling your platform in the region, or a technical integration at minimum. Who handles partnerships?",
        received_at="2026-08-04T12:00:00+05:30"
    )
    assert res["should_skip"] is False
    assert res["assignee_id"] == "u_karan"
    assert res["category"] == "alliances"
    assert res["priority"] == "medium"
    assert res["due_date"] is None
    assert res["deal_value_inr"] is None
    assert res["company_name"] == "Zenith Cloud Partners"


def test_example_7_out_of_office():
    res = determine_routing(
        from_name="Raghav Sharma",
        from_email="raghav@northbridge.in",
        subject="Automatic reply: Out of Office",
        body="I am out of office until 14th August with limited access to email. For urgent matters please contact my colleague at raghav@northbridge.in. — Sent from Outlook",
        received_at="2026-08-03T08:00:00+05:30"
    )
    assert res["should_skip"] is True
    assert res["skip_reason"] == "out_of_office"


def test_example_8_vendor_spam():
    res = determine_routing(
        from_name="Alex Growth",
        from_email="alex@rankboosters.io",
        subject="Quick question regarding organic traffic",
        body="Hi, I noticed your website isn't ranking on page 1 for key terms. We've helped 200+ SaaS companies 3x their organic traffic. We do content marketing, PR outreach, and webinar promotion. Free audit attached — interested in a quick 15 min call?",
        received_at="2026-08-04T15:10:00+05:30"
    )
    assert res["should_skip"] is True
    assert res["skip_reason"] == "vendor_spam"


def test_example_9_newsletter():
    res = determine_routing(
        from_name="B2B Growth Weekly",
        from_email="newsletter@b2bgrowth.co",
        subject="The B2B Growth Weekly — Issue #212",
        body="The B2B Growth Weekly — Issue #212. In this edition: why PLG is stalling, 5 pricing experiments that worked, and a teardown of Figma's onboarding. [Unsubscribe]",
        received_at="2026-08-05T07:30:00+05:30"
    )
    assert res["should_skip"] is True
    assert res["skip_reason"] == "newsletter"


def test_example_10_thread_reply():
    # Follow-up on Example 1: increased budget to 32 lakh, deadline 11th Aug, received 09 Aug -> 48h -> high
    res = determine_routing(
        from_name="Suresh Kulkarni",
        from_email="s.kulkarni@meridiansteel.co.in",
        subject="Re: RFP - Enterprise Document Management System",
        body="Correction to our earlier note — the board has approved an increased budget of Rs. 32 lakhs, and the submission deadline is advanced to 11th August. Apologies for the change.\n\nOn 01 Aug 2026, Suresh Kulkarni wrote:\n> Meridian Steel invites proposals for an enterprise DMS covering 4 plants...",
        received_at="2026-08-09T10:00:00+05:30",
        is_reply=True
    )
    assert res["should_skip"] is False
    assert res["deal_value_inr"] == 3200000
    assert res["due_date"] == "2026-08-11"
    assert res["priority"] == "high"


def test_example_11_genuinely_ambiguous():
    res = determine_routing(
        from_name="Farhan Qureshi",
        from_email="farhan@halcyonretail.com",
        subject="Follow up from Mumbai Booth",
        body="Hi — we met at your booth in Mumbai. Two things: (1) we'd like to evaluate your platform for our 800-person org, budget TBD but likely significant, and (2) our CMO wants to co-host a webinar with your team in September. Can you loop in the right people? — Farhan Qureshi, VP Strategy, Halcyon Retail",
        received_at="2026-08-05T14:40:00+05:30"
    )
    assert res["should_skip"] is False
    assert res["assignee_id"] == "u_triage"
    assert res["category"] == "triage"
    assert res["confidence"] <= 0.45
    assert res["company_name"] == "Halcyon Retail"


def test_example_12_hinglish_crore():
    res = determine_routing(
        from_name="Vikram Sethi",
        from_email="vikram77@gmail.com",
        subject="Product requirement",
        body="Bhai, humko aapka product chahiye for our dealer network. Around 150 users honge. Budget approx 1.2 cr allocated hai for this FY. Kab connect kar sakte hain? Thoda jaldi, board review 20th ko hai.",
        received_at="2026-08-05T16:20:00+05:30"
    )
    assert res["should_skip"] is False
    assert res["assignee_id"] == "u_aarti"
    assert res["category"] == "enterprise_rfp"
    assert res["deal_value_inr"] == 12000000
    assert res["due_date"] == "2026-08-20"
    assert res["company_name"] is None  # Should NOT invent company from personal gmail
