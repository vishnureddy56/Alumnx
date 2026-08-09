import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import InputSection from './components/InputSection';
import RawInboxTable from './components/RawInboxTable';
import ResultsTable from './components/ResultsTable';
import AnalyticsSection from './components/AnalyticsSection';
import ChatAssistant from './components/ChatAssistant';
import { checkHealth, ingestEmails, fetchApiTasks, fetchStats } from './services/api';

// Initial 12 Worked Examples for quick loading
const WORKED_12_CASES = [
  {
    "email_id": "em_00142",
    "thread_id": "th_0091",
    "message_index": 0,
    "from_name": "Suresh Kulkarni",
    "from_email": "s.kulkarni@meridiansteel.co.in",
    "subject": "RFP - Enterprise Document Management System",
    "body": "Meridian Steel invites proposals for an enterprise DMS covering 4 plants and ~1,200 users. Indicative budget is Rs. 25 lakhs. Proposals must reach us by 12th August 2026.",
    "received_at": "2026-08-01T09:14:22+05:30",
    "is_reply": false
  },
  {
    "email_id": "em_00143",
    "thread_id": "th_0092",
    "message_index": 0,
    "from_name": "Ankit Bose",
    "from_email": "ankit@railyardlogistics.in",
    "subject": "Quick demo request",
    "body": "Hi, we're a 30-person logistics startup in Pune... can we get a demo sometime next week? Nothing urgent. — Ankit Bose, Founder, Railyard Logistics",
    "received_at": "2026-08-01T11:02:10+05:30",
    "is_reply": false
  },
  {
    "email_id": "em_00144",
    "thread_id": "th_0093",
    "message_index": 0,
    "from_name": "Procurement Officer",
    "from_email": "tender.desk@bhel.in",
    "subject": "Tender Notice No. BHEL/PROC/2026/0847",
    "body": "Tender Notice No. BHEL/PROC/2026/0847. Bharat Heavy Electricals Limited invites bids for supply of analytics software licences. Estimated value: Rs. 6,50,000. Last date for bid submission: 03-08-2026, 1700 hrs IST.",
    "received_at": "2026-08-01T14:20:00+05:30",
    "is_reply": false
  },
  {
    "email_id": "em_00145",
    "thread_id": "th_0094",
    "message_index": 0,
    "from_name": "Nandita Reddy",
    "from_email": "nandita@saassummit.in",
    "subject": "Sponsorship confirmation needed",
    "body": "We're finalising sponsors for the India SaaS Summit in Bengaluru. Gold tier is ₹4,00,000 and includes a keynote slot. We need confirmation by tomorrow EOD as we're going to print. — Nandita Reddy, Sponsorship Lead",
    "received_at": "2026-08-02T16:45:00+05:30",
    "is_reply": false
  },
  {
    "email_id": "em_00146",
    "thread_id": "th_0095",
    "message_index": 0,
    "from_name": "Accounts Dept",
    "from_email": "billing@vantagecloud.com",
    "subject": "Overdue invoice INV-2026-0331",
    "body": "Please find attached invoice INV-2026-0331 for Rs. 1,18,000 (incl. 18% GST) against PO-88214. Kindly process — payment terms were Net 30 and this is now 12 days overdue. Also, our GSTIN has changed, updated details attached.",
    "received_at": "2026-08-03T10:30:00+05:30",
    "is_reply": false
  },
  {
    "email_id": "em_00147",
    "thread_id": "th_0096",
    "message_index": 0,
    "from_name": "Tariq Mansoor",
    "from_email": "tariq@zenithcloudpartners.com",
    "subject": "Partner Collaboration & Reselling Opportunity",
    "body": "We're a Salesforce implementation partner across MEA with 40+ enterprise clients. We'd like to explore reselling your platform in the region, or a technical integration at minimum. Who handles partnerships?",
    "received_at": "2026-08-04T12:00:00+05:30",
    "is_reply": false
  },
  {
    "email_id": "em_00148",
    "thread_id": "th_0097",
    "message_index": 0,
    "from_name": "Raghav Sharma",
    "from_email": "raghav@northbridge.in",
    "subject": "Automatic reply: Out of Office",
    "body": "I am out of office until 14th August with limited access to email. For urgent matters please contact my colleague at raghav@northbridge.in. — Sent from Outlook",
    "received_at": "2026-08-03T08:00:00+05:30",
    "is_reply": false
  },
  {
    "email_id": "em_00149",
    "thread_id": "th_0098",
    "message_index": 0,
    "from_name": "Alex Growth",
    "from_email": "alex@rankboosters.io",
    "subject": "Quick question regarding organic traffic",
    "body": "Hi, I noticed your website isn't ranking on page 1 for key terms. We've helped 200+ SaaS companies 3x their organic traffic. We do content marketing, PR outreach, and webinar promotion. Free audit attached — interested in a quick 15 min call?",
    "received_at": "2026-08-04T15:10:00+05:30",
    "is_reply": false
  },
  {
    "email_id": "em_00150",
    "thread_id": "th_0099",
    "message_index": 0,
    "from_name": "B2B Growth Weekly",
    "from_email": "newsletter@b2bgrowth.co",
    "subject": "The B2B Growth Weekly — Issue #212",
    "body": "The B2B Growth Weekly — Issue #212. In this edition: why PLG is stalling, 5 pricing experiments that worked, and a teardown of Figma's onboarding. [Unsubscribe]",
    "received_at": "2026-08-05T07:30:00+05:30",
    "is_reply": false
  },
  {
    "email_id": "em_00151",
    "thread_id": "th_0091",
    "message_index": 1,
    "from_name": "Suresh Kulkarni",
    "from_email": "s.kulkarni@meridiansteel.co.in",
    "subject": "Re: RFP - Enterprise Document Management System",
    "body": "Correction to our earlier note — the board has approved an increased budget of Rs. 32 lakhs, and the submission deadline is advanced to 11th August. Apologies for the change.\n\nOn 01 Aug 2026, Suresh Kulkarni wrote:\n> Meridian Steel invites proposals for an enterprise DMS covering 4 plants...",
    "received_at": "2026-08-09T10:00:00+05:30",
    "is_reply": true
  },
  {
    "email_id": "em_00152",
    "thread_id": "th_0100",
    "message_index": 0,
    "from_name": "Farhan Qureshi",
    "from_email": "farhan@halcyonretail.com",
    "subject": "Follow up from Mumbai Booth",
    "body": "Hi — we met at your booth in Mumbai. Two things: (1) we'd like to evaluate your platform for our 800-person org, budget TBD but likely significant, and (2) our CMO wants to co-host a webinar with your team in September. Can you loop in the right people? — Farhan Qureshi, VP Strategy, Halcyon Retail",
    "received_at": "2026-08-05T14:40:00+05:30",
    "is_reply": false
  },
  {
    "email_id": "em_00153",
    "thread_id": "th_0101",
    "message_index": 0,
    "from_name": "Vikram Sethi",
    "from_email": "vikram77@gmail.com",
    "subject": "Product requirement",
    "body": "Bhai, humko aapka product chahiye for our dealer network. Around 150 users honge. Budget approx 1.2 cr allocated hai for this FY. Kab connect kar sakte hain? Thoda jaldi, board review 20th ko hai.",
    "received_at": "2026-08-05T16:20:00+05:30",
    "is_reply": false
  }
];

export default function App() {
  const [candidateId, setCandidateId] = useState('saisradha888@gmail.com');
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [jsonInput, setJsonInput] = useState('');
  const [previewEmails, setPreviewEmails] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [ingestSummary, setIngestSummary] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [processedEmails, setProcessedEmails] = useState([]);
  const [stats, setStats] = useState(null);
  const [sample250Data, setSample250Data] = useState([]);

  // Load sample dataset
  useEffect(() => {
    // Set initial preview to worked cases
    setJsonInput(JSON.stringify(WORKED_12_CASES, null, 2));
    setPreviewEmails(WORKED_12_CASES);

    // Fetch sample_inbox.json if available
    fetch('/sample_inbox.json')
      .then(res => res.json())
      .then(data => setSample250Data(data))
      .catch(() => setSample250Data(WORKED_12_CASES));

    // Poll backend health & load initial data
    const refreshData = async () => {
      const health = await checkHealth();
      setBackendStatus(health.status === 'healthy' ? 'healthy' : 'offline');

      if (health.status === 'healthy') {
        try {
          const apiTasksData = await fetchApiTasks(candidateId);
          setTasks(apiTasksData.tasks || []);
          setProcessedEmails(apiTasksData.processed_emails || []);

          const statsData = await fetchStats(candidateId);
          setStats(statsData);
        } catch (e) {
          console.error(e);
        }
      }
    };

    refreshData();
  }, [candidateId]);

  const handleIngest = async (emailsList) => {
    setIsLoading(true);
    try {
      const summary = await ingestEmails(candidateId, emailsList);
      setIngestSummary(summary);

      // Refresh tasks and stats
      const apiTasksData = await fetchApiTasks(candidateId);
      setTasks(apiTasksData.tasks || []);
      setProcessedEmails(apiTasksData.processed_emails || []);

      const statsData = await fetchStats(candidateId);
      setStats(statsData);
    } catch (err) {
      alert(`Ingest failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1360px', margin: '0 auto', padding: '24px 20px' }}>
      <Header
        candidateId={candidateId}
        setCandidateId={setCandidateId}
        backendStatus={backendStatus}
      />

      <InputSection
        jsonInput={jsonInput}
        setJsonInput={setJsonInput}
        onParsePreview={setPreviewEmails}
        onIngest={handleIngest}
        isLoading={isLoading}
        ingestSummary={ingestSummary}
        sample250Data={sample250Data.length > 0 ? sample250Data : WORKED_12_CASES}
        worked12Data={WORKED_12_CASES}
      />

      <RawInboxTable emails={previewEmails} />

      <ResultsTable tasks={tasks} processedEmails={processedEmails} />

      <AnalyticsSection stats={stats} />

      <ChatAssistant candidateId={candidateId} />
    </div>
  );
}
