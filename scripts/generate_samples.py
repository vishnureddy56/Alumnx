import json
import os
import random

SAMPLE_EMAILS = [
    # 1. Worked Example 1: Clean enterprise RFP
    {
        "email_id": "em_00142",
        "thread_id": "th_0091",
        "message_index": 0,
        "from_name": "Suresh Kulkarni",
        "from_email": "s.kulkarni@meridiansteel.co.in",
        "to": "sales@company.com",
        "cc": ["procurement@meridiansteel.co.in"],
        "subject": "RFP - Enterprise Document Management System",
        "body": "Meridian Steel invites proposals for an enterprise DMS covering 4 plants and ~1,200 users. Indicative budget is Rs. 25 lakhs. Proposals must reach us by 12th August 2026.",
        "received_at": "2026-08-01T09:14:22+05:30",
        "attachments": ["RFP_DMS_2026.pdf"],
        "is_reply": False
    },
    # 2. Worked Example 2: SMB demo request, no value stated
    {
        "email_id": "em_00143",
        "thread_id": "th_0092",
        "message_index": 0,
        "from_name": "Ankit Bose",
        "from_email": "ankit@railyardlogistics.in",
        "to": "sales@company.com",
        "cc": [],
        "subject": "Quick demo request",
        "body": "Hi, we're a 30-person logistics startup in Pune... can we get a demo sometime next week? Nothing urgent. — Ankit Bose, Founder, Railyard Logistics",
        "received_at": "2026-08-01T11:02:10+05:30",
        "attachments": [],
        "is_reply": False
    },
    # 3. Worked Example 3: PSU tender below threshold
    {
        "email_id": "em_00144",
        "thread_id": "th_0093",
        "message_index": 0,
        "from_name": "Procurement Officer",
        "from_email": "tender.desk@bhel.in",
        "to": "sales@company.com",
        "cc": [],
        "subject": "Tender Notice No. BHEL/PROC/2026/0847",
        "body": "Tender Notice No. BHEL/PROC/2026/0847. Bharat Heavy Electricals Limited invites bids for supply of analytics software licences. Estimated value: Rs. 6,50,000. Last date for bid submission: 03-08-2026, 1700 hrs IST.",
        "received_at": "2026-08-01T14:20:00+05:30",
        "attachments": ["NIT_BHEL_0847.pdf"],
        "is_reply": False
    },
    # 4. Worked Example 4: Marketing sponsorship, hard deadline
    {
        "email_id": "em_00145",
        "thread_id": "th_0094",
        "message_index": 0,
        "from_name": "Nandita Reddy",
        "from_email": "nandita@saassummit.in",
        "to": "marketing@company.com",
        "cc": [],
        "subject": "Sponsorship confirmation needed",
        "body": "We're finalising sponsors for the India SaaS Summit in Bengaluru. Gold tier is ₹4,00,000 and includes a keynote slot. We need confirmation by tomorrow EOD as we're going to print. — Nandita Reddy, Sponsorship Lead",
        "received_at": "2026-08-02T16:45:00+05:30",
        "attachments": ["Sponsorship_Deck.pdf"],
        "is_reply": False
    },
    # 5. Worked Example 5: Finance
    {
        "email_id": "em_00146",
        "thread_id": "th_0095",
        "message_index": 0,
        "from_name": "Accounts Dept",
        "from_email": "billing@vantagecloud.com",
        "to": "finance@company.com",
        "cc": [],
        "subject": "Overdue invoice INV-2026-0331",
        "body": "Please find attached invoice INV-2026-0331 for Rs. 1,18,000 (incl. 18% GST) against PO-88214. Kindly process — payment terms were Net 30 and this is now 12 days overdue. Also, our GSTIN has changed, updated details attached.",
        "received_at": "2026-08-03T10:30:00+05:30",
        "attachments": ["INV-2026-0331.pdf", "GSTIN_Certificate.pdf"],
        "is_reply": False
    },
    # 6. Worked Example 6: Alliances
    {
        "email_id": "em_00147",
        "thread_id": "th_0096",
        "message_index": 0,
        "from_name": "Tariq Mansoor",
        "from_email": "tariq@zenithcloudpartners.com",
        "to": "partners@company.com",
        "cc": [],
        "subject": "Partner Collaboration & Reselling Opportunity",
        "body": "We're a Salesforce implementation partner across MEA with 40+ enterprise clients. We'd like to explore reselling your platform in the region, or a technical integration at minimum. Who handles partnerships?",
        "received_at": "2026-08-04T12:00:00+05:30",
        "attachments": [],
        "is_reply": False
    },
    # 7. Worked Example 7: Out-of-office (NO TASK)
    {
        "email_id": "em_00148",
        "thread_id": "th_0097",
        "message_index": 0,
        "from_name": "Raghav Sharma",
        "from_email": "raghav@northbridge.in",
        "to": "sales@company.com",
        "cc": [],
        "subject": "Automatic reply: Out of Office",
        "body": "I am out of office until 14th August with limited access to email. For urgent matters please contact my colleague at raghav@northbridge.in. — Sent from Outlook",
        "received_at": "2026-08-03T08:00:00+05:30",
        "attachments": [],
        "is_reply": False
    },
    # 8. Worked Example 8: Vendor spam disguised as marketing (NO TASK)
    {
        "email_id": "em_00149",
        "thread_id": "th_0098",
        "message_index": 0,
        "from_name": "Alex Growth",
        "from_email": "alex@rankboosters.io",
        "to": "sales@company.com",
        "cc": [],
        "subject": "Quick question regarding organic traffic",
        "body": "Hi, I noticed your website isn't ranking on page 1 for key terms. We've helped 200+ SaaS companies 3x their organic traffic. We do content marketing, PR outreach, and webinar promotion. Free audit attached — interested in a quick 15 min call?",
        "received_at": "2026-08-04T15:10:00+05:30",
        "attachments": ["SEO_Audit_Report.pdf"],
        "is_reply": False
    },
    # 9. Worked Example 9: Newsletter (NO TASK)
    {
        "email_id": "em_00150",
        "thread_id": "th_0099",
        "message_index": 0,
        "from_name": "B2B Growth Weekly",
        "from_email": "newsletter@b2bgrowth.co",
        "to": "sales@company.com",
        "cc": [],
        "subject": "The B2B Growth Weekly — Issue #212",
        "body": "The B2B Growth Weekly — Issue #212. In this edition: why PLG is stalling, 5 pricing experiments that worked, and a teardown of Figma's onboarding. [Unsubscribe]",
        "received_at": "2026-08-05T07:30:00+05:30",
        "attachments": [],
        "is_reply": False
    },
    # 10. Worked Example 10: Thread reply (PATCH, NOT POST)
    {
        "email_id": "em_00151",
        "thread_id": "th_0091",
        "message_index": 1,
        "from_name": "Suresh Kulkarni",
        "from_email": "s.kulkarni@meridiansteel.co.in",
        "to": "sales@company.com",
        "cc": ["procurement@meridiansteel.co.in"],
        "subject": "Re: RFP - Enterprise Document Management System",
        "body": "Correction to our earlier note — the board has approved an increased budget of Rs. 32 lakhs, and the submission deadline is advanced to 11th August. Apologies for the change.\n\nOn 01 Aug 2026, Suresh Kulkarni wrote:\n> Meridian Steel invites proposals for an enterprise DMS covering 4 plants and ~1,200 users. Indicative budget is Rs. 25 lakhs...",
        "received_at": "2026-08-09T10:00:00+05:30",
        "attachments": [],
        "is_reply": True
    },
    # 11. Worked Example 11: Genuinely ambiguous (TRIAGE)
    {
        "email_id": "em_00152",
        "thread_id": "th_0100",
        "message_index": 0,
        "from_name": "Farhan Qureshi",
        "from_email": "farhan@halcyonretail.com",
        "to": "sales@company.com",
        "cc": [],
        "subject": "Follow up from Mumbai Booth",
        "body": "Hi — we met at your booth in Mumbai. Two things: (1) we'd like to evaluate your platform for our 800-person org, budget TBD but likely significant, and (2) our CMO wants to co-host a webinar with your team in September. Can you loop in the right people? — Farhan Qureshi, VP Strategy, Halcyon Retail",
        "received_at": "2026-08-05T14:40:00+05:30",
        "attachments": [],
        "is_reply": False
    },
    # 12. Worked Example 12: Hinglish, informal, value in shorthand
    {
        "email_id": "em_00153",
        "thread_id": "th_0101",
        "message_index": 0,
        "from_name": "Vikram Sethi",
        "from_email": "vikram77@gmail.com",
        "to": "sales@company.com",
        "cc": [],
        "subject": "Product requirement",
        "body": "Bhai, humko aapka product chahiye for our dealer network. Around 150 users honge. Budget approx 1.2 cr allocated hai for this FY. Kab connect kar sakte hain? Thoda jaldi, board review 20th ko hai.",
        "received_at": "2026-08-05T16:20:00+05:30",
        "attachments": [],
        "is_reply": False
    }
]


def generate_extended_samples(total=250):
    emails = list(SAMPLE_EMAILS)

    company_names = [
        ("Tata Consultancy", "tataconsultancy.com", "enterprise"),
        ("Infosys BPM", "infosysbpm.com", "enterprise"),
        ("Swiggy Delivery Ops", "swiggy.in", "smb"),
        ("Zomato Fleet", "zomato.com", "smb"),
        ("Reliance Jio Platforms", "jio.com", "enterprise"),
        ("Razorpay Payments", "razorpay.com", "fintech"),
        ("Zerodha Broking", "zerodha.com", "fintech"),
        ("Zepto Express", "zeptonow.com", "smb"),
        ("Delhivery Logistics", "delhivery.com", "enterprise"),
        ("NTPC Power Corp", "ntpc.co.in", "psu"),
        ("ONGC Petro", "ongc.co.in", "psu"),
        ("SAIL Steel Authority", "sail.gov.in", "psu")
    ]

    first_names = ["Rahul", "Pooja", "Arun", "Sneha", "Kavita", "Amit", "Deepak", "Rohan", "Ananya", "Manoj"]
    last_names = ["Deshmukh", "Nair", "Patel", "Verma", "Chawla", "Gupta", "Menon", "Reddy", "Mehta", "Iyer"]

    types_pool = [
        "enterprise_rfp", "smb_demo", "marketing_sponsorship", "alliances",
        "finance_invoice", "vendor_spam", "ooo", "newsletter", "triage_ambiguous"
    ]

    for i in range(len(emails) + 1, total + 1):
        idx_str = f"{i:05d}"
        thread_num = f"{random.randint(102, 280):04d}"
        c_name, c_domain, c_type = random.choice(company_names)
        f_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        f_email = f"{f_name.lower().replace(' ', '.')}@{c_domain}"

        category_type = random.choice(types_pool)

        if category_type == "enterprise_rfp":
            budget_lakhs = random.randint(15, 80)
            budget_str = f"Rs. {budget_lakhs} lakhs" if random.random() > 0.5 else f"₹{budget_lakhs}L"
            day = random.randint(10, 28)
            subject = f"RFP: Enterprise License Procurement - {c_name}"
            body = f"Dear Sales Team,\n\n{c_name} is releasing an RFP for expanding our software infrastructure. Estimated budget allocated is {budget_str}. Please submit formal proposals by {day}th August 2026.\n\nRegards,\n{f_name}"
            attachments = [f"RFP_{c_name.replace(' ', '_')}.pdf"]
        elif category_type == "smb_demo":
            subject = f"Demo request for our 25-member team"
            body = f"Hi Team,\n\nWe would love to see a live demo of your workflow solution next week. Nothing urgent, looking to understand features.\n\nThanks,\n{f_name}, {c_name}"
            attachments = []
        elif category_type == "marketing_sponsorship":
            cost = random.randint(2, 8) * 100000
            subject = f"Keynote Sponsor Invitation - Tech Summit 2026"
            body = f"Hi Marketing Team,\n\nInviting your company to be a Gold Sponsor at our annual summit in Bangalore. Tier cost is ₹{cost:,}. Kindly confirm by tomorrow EOD.\n\nBest,\n{f_name}, Sponsorship Chair"
            attachments = ["Event_Brochure.pdf"]
        elif category_type == "alliances":
            subject = f"Channel Partner & Integration discussion"
            body = f"Hello,\n\nWe are an authorized solution partner with 20+ enterprise deployments in Western India. We want to discuss reselling your product and API integrations.\n\nCheers,\n{f_name}"
            attachments = []
        elif category_type == "finance_invoice":
            inv_num = random.randint(1000, 9999)
            amt = random.randint(50, 450) * 1000
            subject = f"Invoice INV-2026-{inv_num} for processing"
            body = f"Please find attached our tax invoice INV-2026-{inv_num} for Rs. {amt:,} against PO-4482. Payment is overdue by 5 days. Please expedite.\n\nAccounts Team"
            attachments = [f"INV_{inv_num}.pdf"]
        elif category_type == "vendor_spam":
            subject = f"Boost your Google Rankings 10x"
            body = f"Hi,\n\nWe noticed your domain is missing backlinks. We've helped 200+ SaaS companies grow organic traffic with PR outreach and content marketing. Free audit attached. Let's schedule a 15 min call.\n\n{f_name}"
            attachments = ["SEO_Report.pdf"]
        elif category_type == "ooo":
            subject = f"Automatic reply: Out of Office"
            body = f"I am currently away from the office with limited email connectivity. For immediate queries, contact info@company.com. — Sent from Outlook"
            attachments = []
        elif category_type == "newsletter":
            subject = f"SaaS Insider Weekly — Issue #{random.randint(100, 500)}"
            body = f"This week in B2B SaaS: Retention strategies and pricing models teardown. Click here to [Unsubscribe]."
            attachments = []
        else:
            subject = f"General Inquiry - Multiple Needs"
            body = f"Hello, we met at the conference. We want to test your platform for our team (budget TBD), and also our VP Marketing wants to explore co-hosting a webinar with you. Who can help?\n\n{f_name}, {c_name}"
            attachments = []

        day_rec = random.randint(1, 8)
        hour_rec = random.randint(9, 18)
        min_rec = random.randint(10, 59)
        received_at = f"2026-08-{day_rec:02d}T{hour_rec:02d}:{min_rec:02d}:00+05:30"

        emails.append({
            "email_id": f"em_{idx_str}",
            "thread_id": f"th_{thread_num}",
            "message_index": 0,
            "from_name": f_name,
            "from_email": f_email,
            "to": "sales@company.com",
            "cc": [],
            "subject": subject,
            "body": body,
            "received_at": received_at,
            "attachments": attachments,
            "is_reply": False
        })

    return emails


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "sample_inbox.json")
    dataset = generate_extended_samples(250)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    print(f"Generated {len(dataset)} sample emails in {out_file}")
