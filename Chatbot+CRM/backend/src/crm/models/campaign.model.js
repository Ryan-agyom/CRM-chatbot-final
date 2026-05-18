export function createCampaignModel(data) {
  return {
    id: data.id,
    name: data.name,
    segment: data.segment,
    message: data.message,
    trigger: data.trigger,
    createdAt: data.createdAt
  };
}
