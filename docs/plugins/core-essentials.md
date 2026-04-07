# Core Essentials

Core Essentials, SMP ve network sunuculari icin temel yonetim araclarini sunar.

## Kurulum

1. `WaveCoreEssentials-x.x.x.jar` dosyasini `plugins/` klasorune atin.
2. Sunucuyu baslatin, dosyalar olussun.
3. `plugins/WaveCoreEssentials/config.yml` dosyasini duzenleyin.
4. `/wce reload` ile ayarlari yenileyin.

## Komutlar

| Komut | Aciklama | Yetki |
| --- | --- | --- |
| `/sethome <isim>` | Yeni home kaydeder | Oyuncu |
| `/home <isim>` | Home'a isinlar | Oyuncu |
| `/spawn` | Spawn noktasina doner | Oyuncu |
| `/wce reload` | Plugini yeniden yukler | Admin |

## Permission Node'lari

```txt
wavesetups.core.home
wavesetups.core.sethome
wavesetups.core.spawn
wavesetups.core.reload
wavesetups.core.admin
```

## Ornek Config

```yaml
prefix: "&bWaveSetups &8>>"
max-homes: 3
spawn-on-join: true
cooldowns:
  home: 5
  spawn: 10
```

## Sorun Giderme

- `Unknown command` hatasi aliyorsan plugin aktif degil olabilir. Sunucu logunu kontrol et.
- Teleport buglari icin baska bir essentials plugin'i ile cakisma var mi bak.
