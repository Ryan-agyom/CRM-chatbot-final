export function createLeadModel(data) {
  return {
    id: data.id,
    name: data.name,
    email: data.email,
    phone: data.phone,
    requirements: data.requirements,
    source: data.source,
    createdAt: data.createdAt
  };
}
