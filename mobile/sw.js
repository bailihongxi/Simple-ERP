// Service Worker - 进销存手机版
const CACHE_NAME = 'simple-erp-v1';
const urlsToCache = [
    './',
    './index.html',
    './manifest.json',
    './css/style.css',
    './js/app.js',
    './js/storage.js'
];

// 安装：预缓存静态文件
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(urlsToCache);
        }).then(function() {
            return self.skipWaiting();
        })
    );
});

// 激活：清理旧缓存
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(cacheName) {
                    return cacheName !== CACHE_NAME;
                }).map(function(cacheName) {
                    return caches.delete(cacheName);
                })
            );
        }).then(function() {
            return self.clients.claim();
        })
    );
});

// 请求：缓存优先策略
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            // 缓存命中，返回缓存
            if (response) {
                return response;
            }
            // 缓存未命中，请求网络
            return fetch(event.request).then(function(response) {
                // 检查是否是有效的响应
                if (!response || response.status !== 200 || response.type !== 'basic') {
                    return response;
                }
                // 克隆响应，一份返回，一份存入缓存
                var responseToCache = response.clone();
                caches.open(CACHE_NAME).then(function(cache) {
                    cache.put(event.request, responseToCache);
                });
                return response;
            }).catch(function() {
                // 网络失败，返回离线页面
                return caches.match('./index.html');
            });
        })
    );
});
