import { defineConfig } from 'vitepress'

// https://vitepress.vuejs.org/config/app-configs
export default defineConfig({
  lang: 'tr-TR',
  title: 'WaveSetups Docs',
  description: 'Minecraft pluginleri ve plugin paketleri icin resmi dokumantasyon merkezi.',
  cleanUrls: true,
  themeConfig: {
    logo: '/logo.svg',
    nav: [
      { text: 'Baslangic', link: '/getting-started' },
      { text: 'Pluginler', link: '/plugins/' },
      { text: 'Paketler', link: '/bundles/' },
      { text: 'SSS', link: '/faq' },
      { text: 'Discord', link: 'https://discord.gg/wavesetups' }
    ],
    sidebar: [
      {
        text: 'Genel',
        items: [
          { text: 'Hizli Baslangic', link: '/getting-started' },
          { text: 'Destek Kurallari', link: '/support' },
          { text: 'SSS', link: '/faq' }
        ]
      },
      {
        text: 'Plugin Dokumantasyonlari',
        items: [
          { text: 'Tum Pluginler', link: '/plugins/' },
          { text: 'Core Essentials', link: '/plugins/core-essentials' },
          { text: 'Lobby System', link: '/plugins/lobby-system' }
        ]
      },
      {
        text: 'Plugin Paketleri',
        items: [
          { text: 'Tum Paketler', link: '/bundles/' },
          { text: 'SkyBlock Paket', link: '/bundles/skyblock-pack' }
        ]
      },
      {
        text: 'Guncellemeler',
        items: [{ text: 'Changelog', link: '/changelog' }]
      }
    ],
    socialLinks: [
      { icon: 'discord', link: 'https://discord.gg/wavesetups' }
    ],
    footer: {
      message: 'WaveSetups tarafindan sevgiyle gelistirildi.',
      copyright: 'Copyright (c) 2026 WaveSetups'
    },
    outline: [2, 3],
    search: {
      provider: 'local'
    }
  }
})
