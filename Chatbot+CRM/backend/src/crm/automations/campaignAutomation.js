export const campaignAutomation = {
  schedule(campaign) {
    return {
      campaignId: campaign.id,
      status: "scheduled"
    };
  }
};
