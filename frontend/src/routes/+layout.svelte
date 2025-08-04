<script lang="ts">
	import '../app.css';
</script>

<div class="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
	<nav class="bg-gray-800/50 backdrop-blur-sm border-b border-purple-500/30">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex items-center justify-between h-16">
				<div class="flex items-center">
					<h1 class="text-2xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
						GuildedIn
					</h1>
				</div>
				<div class="flex space-x-4">
					<a href="/" class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Home</a>
					<a href="/guilds" class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Guilds</a>
					<a href="/dungeons" class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Dungeons</a>
					<a href="/profile" class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Profile</a>
				</div>
			</div>
		</div>
	</nav>
	
	<main>
		<slot />
	</main>
</div>