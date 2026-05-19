export default function DevOpsAIDashboard() {
  const metrics = [
    { title: 'CPU Usage', value: '43%' },
    { title: 'RAM Usage', value: '68%' },
    { title: 'Pods Running', value: '12' },
    { title: 'CI/CD Status', value: 'Healthy' },
  ];

  const chats = [
    {
      role: 'assistant',
      message:
        'Bonjour 👋 Je suis votre assistant DevOps IA. Je peux générer du Terraform, Docker, Kubernetes et analyser vos pipelines CI/CD.',
    },
    {
      role: 'user',
      message: 'Génère un déploiement Kubernetes pour mon backend FastAPI.',
    },
    {
      role: 'assistant',
      message:
        'Deployment généré avec succès. ReplicaSet, Service et Ingress inclus.',
    },
  ];

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-black blur-3xl" />

      {/* Navbar */}
      <header className="relative z-10 border-b border-white/10 backdrop-blur-xl bg-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              ChatOps AI Enterprise
            </h1>
            <p className="text-sm text-gray-400">
              DevOps • Kubernetes • AI • Monitoring
            </p>
          </div>

          <div className="flex items-center gap-4">
            <button className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 transition-all shadow-lg shadow-blue-500/20">
              Deploy
            </button>

            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500" />
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="relative z-10 flex h-[calc(100vh-81px)]">
        {/* Sidebar */}
        <aside className="w-72 border-r border-white/10 bg-white/5 backdrop-blur-xl p-5 flex flex-col">
          <div className="mb-8">
            <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl py-3 font-semibold hover:scale-[1.02] transition-all">
              + New Conversation
            </button>
          </div>

          <nav className="space-y-2">
            {[
              'AI Chat',
              'Monitoring',
              'Kubernetes',
              'Terraform',
              'CI/CD Pipelines',
              'Security Center',
              'Logs Explorer',
              'Settings',
            ].map((item) => (
              <button
                key={item}
                className="w-full text-left px-4 py-3 rounded-xl hover:bg-white/10 transition-all text-gray-300 hover:text-white"
              >
                {item}
              </button>
            ))}
          </nav>

          <div className="mt-auto border-t border-white/10 pt-4">
            <div className="rounded-2xl bg-gradient-to-br from-blue-600/20 to-purple-600/20 p-4 border border-white/10">
              <h3 className="font-semibold mb-2">AI Infrastructure</h3>
              <p className="text-sm text-gray-400">
                OpenAI • LangChain • Kubernetes • Prometheus
              </p>
            </div>
          </div>
        </aside>

        {/* Content */}
        <section className="flex-1 flex flex-col overflow-hidden">
          {/* Hero */}
          <div className="px-8 pt-8 pb-6 border-b border-white/10 bg-gradient-to-r from-blue-500/10 to-purple-500/10 backdrop-blur-xl">
            <div className="flex items-center justify-between gap-6 flex-wrap">
              <div>
                <h2 className="text-5xl font-bold mb-4 leading-tight">
                  AI DevOps Platform
                </h2>
                <p className="text-gray-300 max-w-2xl text-lg">
                  Plateforme intelligente de monitoring, orchestration cloud,
                  Kubernetes et automatisation DevOps alimentée par une IA.
                </p>
              </div>

              <div className="flex gap-4">
                <button className="px-6 py-3 rounded-2xl bg-blue-600 hover:bg-blue-500 transition-all font-semibold">
                  Start AI Session
                </button>

                <button className="px-6 py-3 rounded-2xl border border-white/20 hover:bg-white/10 transition-all font-semibold">
                  Documentation
                </button>
              </div>
            </div>
          </div>

          {/* Dashboard */}
          <div className="flex-1 overflow-auto p-8 space-y-8">
            {/* Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              {metrics.map((metric) => (
                <div
                  key={metric.title}
                  className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 hover:border-blue-500/30 transition-all"
                >
                  <p className="text-gray-400 mb-3">{metric.title}</p>
                  <h3 className="text-4xl font-bold">{metric.value}</h3>
                </div>
              ))}
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
              {/* AI Chat */}
              <div className="xl:col-span-2 rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl overflow-hidden flex flex-col h-[650px]">
                <div className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-semibold">AI Assistant</h3>
                    <p className="text-sm text-gray-400">
                      Streaming intelligent responses
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-sm text-green-400">Online</span>
                  </div>
                </div>

                <div className="flex-1 overflow-auto p-6 space-y-6">
                  {chats.map((chat, index) => (
                    <div
                      key={index}
                      className={`flex ${
                        chat.role === 'user'
                          ? 'justify-end'
                          : 'justify-start'
                      }`}
                    >
                      <div
                        className={`max-w-[80%] rounded-3xl px-5 py-4 ${
                          chat.role === 'user'
                            ? 'bg-blue-600'
                            : 'bg-white/10 border border-white/10'
                        }`}
                      >
                        <p className="text-sm leading-relaxed">
                          {chat.message}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="border-t border-white/10 p-5">
                  <div className="flex gap-4 items-center">
                    <input
                      type="text"
                      placeholder="Ask your AI DevOps assistant..."
                      className="flex-1 bg-white/10 border border-white/10 rounded-2xl px-5 py-4 outline-none focus:border-blue-500"
                    />

                    <button className="px-6 py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 hover:scale-105 transition-all font-semibold">
                      Send
                    </button>
                  </div>
                </div>
              </div>

              {/* Monitoring */}
              <div className="space-y-6">
                {/* Cluster Status */}
                <div className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-semibold">
                      Kubernetes Cluster
                    </h3>

                    <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-sm">
                      Healthy
                    </span>
                  </div>

                  <div className="space-y-4">
                    {[
                      ['Frontend Pods', '4/4'],
                      ['Backend Pods', '6/6'],
                      ['Workers', '2/2'],
                      ['Ingress', 'Active'],
                    ].map(([label, value]) => (
                      <div
                        key={label}
                        className="flex items-center justify-between"
                      >
                        <span className="text-gray-400">{label}</span>
                        <span className="font-semibold">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* CI/CD */}
                <div className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl p-6">
                  <h3 className="text-xl font-semibold mb-6">
                    CI/CD Pipeline
                  </h3>

                  <div className="space-y-5">
                    {[
                      'Code Analysis',
                      'Unit Tests',
                      'Docker Build',
                      'Security Scan',
                      'Deploy Production',
                    ].map((step) => (
                      <div
                        key={step}
                        className="flex items-center gap-4"
                      >
                        <div className="w-4 h-4 rounded-full bg-green-500" />
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* AI Features */}
                <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-blue-600/20 to-purple-600/20 backdrop-blur-xl p-6">
                  <h3 className="text-xl font-semibold mb-6">
                    AI Features
                  </h3>

                  <div className="space-y-4">
                    {[
                      'RAG Document Analysis',
                      'Terraform Generation',
                      'Kubernetes Assistant',
                      'DevSecOps Analysis',
                      'Monitoring Intelligence',
                    ].map((feature) => (
                      <div
                        key={feature}
                        className="flex items-center gap-3"
                      >
                        <div className="w-2 h-2 rounded-full bg-blue-400" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
