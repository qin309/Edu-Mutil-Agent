<template>
  <div class="knowledge-graph-container">
    <div class="graph-header">
      <div class="header-content">
        <h1>🕸️ 知识图谱</h1>
        <p>可视化显示知识库中的实体关系</p>
      </div>
      <div class="header-actions">
        <n-button type="primary" size="large" @click="refreshGraph" :loading="loading">
          <template #icon>
            <RefreshCw />
          </template>
          刷新图谱
        </n-button>
      </div>
    </div>

    <div class="graph-content">
      <div v-if="loading" class="loading-state">
        <n-spin size="large" />
        <p>正在生成知识图谱...</p>
      </div>

      <div v-else-if="!graphData || !graphData.entities || graphData.entities.length === 0" class="empty-state">
        <div class="empty-content">
          <n-icon size="64" color="var(--text-muted)">
            <Network />
          </n-icon>
          <h3>知识图谱为空</h3>
          <p>需要上传更多文档来构建知识图谱。LightRAG 将自动生成实体和关系。</p>
          <n-button type="primary" @click="$router.push('/knowledge')">
            上传文档
          </n-button>
        </div>
      </div>

      <div v-else class="graph-visualization">
        <div class="graph-controls">
          <n-space>
            <n-button @click="zoomIn" size="small">放大</n-button>
            <n-button @click="zoomOut" size="small">缩小</n-button>
            <n-button @click="resetZoom" size="small">重置</n-button>
          </n-space>
        </div>
        <div ref="graphContainer" class="graph-canvas"></div>
      </div>
    </div>

    <!-- Graph Info Panel -->
    <div v-if="graphData" class="graph-info">
      <div class="info-stats">
        <div class="stat-item">
          <div class="stat-value">{{ graphData.entities?.length || 0 }}</div>
          <div class="stat-label">实体数量</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ graphData.relationships?.length || 0 }}</div>
          <div class="stat-label">关系数量</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ graphData.chunks?.length || 0 }}</div>
          <div class="stat-label">文档块数量</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'naive-ui'
import { RefreshCw, Network } from 'lucide-vue-next'
import { api } from '@/services/api'

interface GraphNode {
  id: string
  label: string
  type: string
  properties?: Record<string, any>
}

interface GraphLink {
  source: string
  target: string
  type: string
  weight?: number
}

interface GraphData {
  entities: GraphNode[]
  relationships: GraphLink[]
  chunks?: any[]
}

const graphContainer = ref<HTMLElement>()
const loading = ref(false)
const graphData = ref<GraphData | null>(null)
const graphInstance = ref<any>(null)

// Enhanced graph visualization using SVG with force-directed layout
const createSimpleGraph = (container: HTMLElement, data: GraphData) => {
  // Clear container
  container.innerHTML = ''

  if (!data.entities || data.entities.length === 0) return

  // Set container size
  const width = Math.max(container.clientWidth || 800, 600)
  const height = Math.max(container.clientHeight || 600, 400)
  container.style.width = width + 'px'
  container.style.height = height + 'px'
  container.style.background = 'linear-gradient(135deg, #1e293b 0%, #334155 100%)'
  container.style.borderRadius = '8px'
  container.style.position = 'relative'
  container.style.overflow = 'hidden'

  // Create SVG
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.setAttribute('width', width.toString())
  svg.setAttribute('height', height.toString())
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`)
  svg.style.display = 'block'
  container.appendChild(svg)

  // Create a simple force-directed layout simulation
  const nodes = data.entities
    .filter(entity => entity.label && entity.id)
    .slice(0, 30) // Limit nodes for performance
    .map(entity => ({
      ...entity,
      x: Math.random() * width * 0.8 + width * 0.1,
      y: Math.random() * height * 0.8 + height * 0.1,
      vx: 0,
      vy: 0
    }))

  const links = data.relationships
    .filter(rel => rel.source && rel.target &&
            nodes.find(n => n.id === rel.source) &&
            nodes.find(n => n.id === rel.target))
    .slice(0, 50) // Limit links for performance

  // Force-directed layout simulation (simple implementation)
  const repelForce = 100
  const attractForce = 0.001
  const centerForce = 0.01
  const iterations = 50

  for (let i = 0; i < iterations; i++) {
    // Reset forces
    nodes.forEach(node => {
      node.vx *= 0.9
      node.vy *= 0.9
    })

    // Apply repulsion between nodes
    for (let a = 0; a < nodes.length; a++) {
      for (let b = a + 1; b < nodes.length; b++) {
        const dx = nodes[b].x - nodes[a].x
        const dy = nodes[b].y - nodes[a].y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = repelForce / (dist * dist + 10)

        nodes[a].vx -= dx * force / dist
        nodes[a].vy -= dy * force / dist
        nodes[b].vx += dx * force / dist
        nodes[b].vy += dy * force / dist
      }
    }

    // Apply attraction along links
    links.forEach(link => {
      const source = nodes.find(n => n.id === link.source)
      const target = nodes.find(n => n.id === link.target)
      if (source && target) {
        const dx = target.x - source.x
        const dy = target.y - source.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = (dist - 120) * attractForce

        source.vx += dx * force / dist
        source.vy += dy * force / dist
        target.vx -= dx * force / dist
        target.vy -= dy * force / dist
      }
    })

    // Apply centering force
    nodes.forEach(node => {
      const dx = width / 2 - node.x
      const dy = height / 2 - node.y
      node.vx += dx * centerForce
      node.vy += dy * centerForce
    })

    // Apply forces
    nodes.forEach(node => {
      node.x += node.vx * 0.3
      node.y += node.vy * 0.3

      // Keep nodes within bounds
      node.x = Math.max(30, Math.min(width - 30, node.x))
      node.y = Math.max(30, Math.min(height - 30, node.y))
    })
  }

  // Create links first (background)
  const linkGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g')
  svg.appendChild(linkGroup)

  links.forEach(link => {
    const source = nodes.find(n => n.id === link.source)
    const target = nodes.find(n => n.id === link.target)

    if (source && target) {
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
      line.setAttribute('x1', source.x.toString())
      line.setAttribute('y1', source.y.toString())
      line.setAttribute('x2', target.x.toString())
      line.setAttribute('y2', target.y.toString())
      line.setAttribute('stroke', 'rgba(255, 255, 255, 0.3)')
      line.setAttribute('stroke-width', '2')
      line.setAttribute('opacity', '0.6')
      linkGroup.appendChild(line)
    }
  })

  // Create nodes
  const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g')
  svg.appendChild(nodeGroup)

  nodes.forEach((node, index) => {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    nodeGroup.appendChild(g)

    // Node circle with different colors based on type
    const getNodeColor = (type: string) => {
      switch (type) {
        case 'concept': return '#10B981'
        case 'tool': return '#3B82F6'
        case 'technology': return '#F59E0B'
        case 'person': return '#EF4444'
        case 'organization': return '#8B5CF6'
        default: return '#6B7280'
      }
    }

    // Create circle
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    circle.setAttribute('cx', node.x.toString())
    circle.setAttribute('cy', node.y.toString())
    circle.setAttribute('r', '16')
    circle.setAttribute('fill', getNodeColor(node.type))
    circle.setAttribute('stroke', '#fff')
    circle.setAttribute('stroke-width', '2')
    circle.style.cursor = 'pointer'
    circle.style.transition = 'all 0.2s ease'

    // Create label
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    text.setAttribute('x', node.x.toString())
    text.setAttribute('y', (node.y - 25).toString())
    text.setAttribute('text-anchor', 'middle')
    text.setAttribute('font-size', '12px')
    text.setAttribute('fill', 'rgba(255, 255, 255, 0.9)')
    text.setAttribute('font-family', 'system-ui, -apple-system, sans-serif')
    text.setAttribute('pointer-events', 'none')
    text.textContent = node.label.length > 15 ? node.label.substring(0, 12) + '...' : node.label

    let highlightTimeout: number

    const highlightNode = () => {
      clearTimeout(highlightTimeout)
      circle.setAttribute('r', '20')
      circle.setAttribute('stroke-width', '3')

      // Highlight connected links and nodes
      links.forEach(link => {
        const source = nodes.find(n => n.id === link.source)
        const target = nodes.find(n => n.id === link.target)

        if (source?.id === node.id && target) {
          const line = linkGroup.children[index] as SVGElement
          if (line) {
            line.setAttribute('stroke', 'rgba(16, 185, 129, 0.8)')
            line.setAttribute('stroke-width', '3')
            line.setAttribute('opacity', '1')
          }
          target.vx *= 1.1 // Temporary effect
          target.vy *= 1.1
        }
      })
    }

    const unhighlightNode = () => {
      highlightTimeout = window.setTimeout(() => {
        circle.setAttribute('r', '16')
        circle.setAttribute('stroke-width', '2')

        // Reset link highlights
        links.forEach(link => {
          const line = linkGroup.children[links.indexOf(link)] as SVGElement
          if (line) {
            line.setAttribute('stroke', 'rgba(255, 255, 255, 0.3)')
            line.setAttribute('stroke-width', '2')
            line.setAttribute('opacity', '0.6')
          }
        })
      }, 100)
    }

    circle.addEventListener('mouseenter', highlightNode)
    circle.addEventListener('mouseleave', unhighlightNode)

    g.appendChild(circle)
    g.appendChild(text)
  })

  // Add zoom and pan functionality
  let isDragging = false
  let startX = 0
  let startY = 0
  let currentTranslateX = 0
  let currentTranslateY = 0
  let currentScale = 1

  const handleMouseDown = (e: MouseEvent) => {
    isDragging = true
    startX = e.clientX - currentTranslateX
    startY = e.clientY - currentTranslateY
    container.style.cursor = 'grabbing'
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return

    currentTranslateX = e.clientX - startX
    currentTranslateY = e.clientY - startY

    nodeGroup.setAttribute('transform', `translate(${currentTranslateX}, ${currentTranslateY}) scale(${currentScale})`)
    linkGroup.setAttribute('transform', `translate(${currentTranslateX}, ${currentTranslateY}) scale(${currentScale})`)
  }

  const handleMouseUp = () => {
    isDragging = false
    container.style.cursor = 'grab'
  }

  const handleWheel = (e: WheelEvent) => {
    e.preventDefault()
    const scaleFactor = e.deltaY > 0 ? 0.9 : 1.1
    currentScale = Math.min(Math.max(0.5, currentScale * scaleFactor), 3)

    nodeGroup.setAttribute('transform', `translate(${currentTranslateX}, ${currentTranslateY}) scale(${currentScale})`)
    linkGroup.setAttribute('transform', `translate(${currentTranslateX}, ${currentTranslateY}) scale(${currentScale})`)
  }

  svg.addEventListener('mousedown', handleMouseDown)
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseup', handleMouseUp)
  svg.addEventListener('wheel', handleWheel)

  container.style.cursor = 'grab'
}

const loadGraph = async () => {
  loading.value = true
  try {
    const response = await api.get('/knowledge/graph')
    graphData.value = response.data

    if (graphContainer.value && graphData.value) {
      createSimpleGraph(graphContainer.value, graphData.value)
    }
  } catch (error: any) {
    console.error('Failed to load graph:', error)
    message.error('加载知识图谱失败')

    // Mock data for demonstration
    graphData.value = {
      entities: [
        { id: '1', label: 'Machine Learning', type: 'concept' },
        { id: '2', label: 'Neural Networks', type: 'concept' },
        { id: '3', label: 'Deep Learning', type: 'concept' },
        { id: '4', label: 'Python', type: 'tool' },
        { id: '5', label: 'TensorFlow', type: 'tool' },
      ],
      relationships: [
        { source: '1', target: '2', type: 'includes' },
        { source: '2', target: '3', type: 'subtype' },
        { source: '1', target: '4', type: 'uses' },
        { source: '3', target: '5', type: 'implements_with' },
      ]
    }

    if (graphContainer.value && graphData.value) {
      createSimpleGraph(graphContainer.value, graphData.value)
    }
  } finally {
    loading.value = false
  }
}

const refreshGraph = () => {
  loadGraph()
}

const zoomIn = () => {
  // Simple zoom logic - would need more sophisticated implementation
  const container = graphContainer.value
  if (container) {
    const currentScale = parseFloat(container.dataset.scale || '1')
    const newScale = Math.min(currentScale * 1.2, 3)
    container.dataset.scale = newScale.toString()
    container.style.transform = `scale(${newScale})`
  }
}

const zoomOut = () => {
  const container = graphContainer.value
  if (container) {
    const currentScale = parseFloat(container.dataset.scale || '1')
    const newScale = Math.max(currentScale / 1.2, 0.5)
    container.dataset.scale = newScale.toString()
    container.style.transform = `scale(${newScale})`
  }
}

const resetZoom = () => {
  const container = graphContainer.value
  if (container) {
    container.dataset.scale = '1'
    container.style.transform = 'scale(1)'
  }
}

onMounted(() => {
  loadGraph()
})
</script>

<style scoped>
.knowledge-graph-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 2rem;
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
}

.header-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.graph-content {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 2rem;
  min-height: 600px;
  position: relative;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  text-align: center;
}

.empty-content h3 {
  margin: 1rem 0 0.5rem 0;
  color: var(--text-primary);
}

.empty-content p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.graph-visualization {
  height: 100%;
  position: relative;
}

.graph-controls {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
  background: rgba(0, 0, 0, 0.5);
  padding: 0.5rem;
  border-radius: 8px;
}

.graph-canvas {
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.graph-info {
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
}

.stat-item {
  text-align: center;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 8px;
  padding: 1rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .graph-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .info-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>