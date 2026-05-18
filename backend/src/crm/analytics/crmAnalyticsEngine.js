export const crmAnalyticsEngine = {
  generate({ leads, campaigns, tickets }) {
    return {
      customerInsights: {
        leadCount: leads.length,
        commonComplaints: tickets.map((ticket) => ticket.issue),
        activeCampaigns: campaigns.length
      },
      predictiveAnalysis: {
        likelyToConvert: leads.filter((lead) => lead.requirements).length,
        likelyToChurn: tickets.length > 5 ? "medium-risk" : "low-risk",
        trendingProducts: ["laptops", "phones", "accessories"]
      }
    };
  }
};
