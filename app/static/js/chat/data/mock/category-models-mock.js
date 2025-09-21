// Mock category models
// Keep this isolated so it can be swapped with real API later

export function getCategoryModelsMock(category) {
  const base = [
    {
      id: 'model-101',
      modelId: 101,
      name: 'Gemini 2.5 Flash',
      model_name: 'gemini-2.5-flash',
      provider: 'Google',
      type: 'multimodal',
      description: 'Hızlı ve hafif multimodal model',
      icon: 'fab fa-google',
      color: '#4285f4'
    },
    {
      id: 'model-201',
      modelId: 201,
      name: 'ChatGPT-4',
      model_name: 'chatgpt-4',
      provider: 'OpenAI',
      type: 'text',
      description: 'Genel amaçlı güçlü sohbet modeli',
      icon: 'fas fa-robot',
      color: '#10a37f'
    },
    {
      id: 'model-301',
      modelId: 301,
      name: 'Claude 3',
      model_name: 'claude-3',
      provider: 'Anthropic',
      type: 'text',
      description: 'Uzun bağlam ve yardımcı yanıtlar',
      icon: 'fas fa-brain',
      color: '#d97706'
    },
    {
      id: 'model-401',
      modelId: 401,
      name: 'DeepSeek Coder',
      model_name: 'deepseek-coder',
      provider: 'DeepSeek',
      type: 'code',
      description: 'Kod üretimi ve hata ayıklama',
      icon: 'fas fa-code',
      color: '#7c3aed'
    }
  ];

  const map = {
    'Programming': ['deepseek-coder', 'chatgpt-4'],
    'Creative Writing': ['claude-3', 'chatgpt-4'],
    'Business': ['chatgpt-4', 'gemini-2.5-flash'],
    'Education': ['gemini-2.5-flash', 'claude-3'],
    'Health & Wellness': ['claude-3'],
    'Gaming': ['gemini-2.5-flash']
  };

  const names = map[category] || base.map(m => m.model_name);
  return base.filter(m => names.includes(m.model_name));
}
