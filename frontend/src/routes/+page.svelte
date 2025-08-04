<script lang="ts">
	import { onMount } from 'svelte';
	
	let apiStatus = 'checking...';
	
	onMount(async () => {
		try {
			const response = await fetch('http://localhost:8000/health');
			const data = await response.json();
			apiStatus = data.status;
		} catch (error) {
			apiStatus = 'offline';
		}
	});
</script>

<svelte:head>
	<title>GuildedIn - Where adventurers find their guild!</title>
</svelte:head>

<div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
	<div class="text-center">
		<h1 class="text-5xl font-extrabold mb-8">
			<span class="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
				Welcome to GuildedIn
			</span>
		</h1>
		<p class="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
			The professional network for adventurers. Find your guild, embark on epic dungeons, 
			and build your legendary career in the realm of adventure!
		</p>
		
		<div class="grid md:grid-cols-3 gap-8 mb-12">
			<div class="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-purple-500/30">
				<div class="text-3xl mb-4">⚔️</div>
				<h3 class="text-xl font-semibold mb-2 text-purple-300">Find Your Class</h3>
				<p class="text-gray-400">Tank, DPS, Healer, or Support - discover your adventuring specialization</p>
			</div>
			
			<div class="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-blue-500/30">
				<div class="text-3xl mb-4">🏰</div>
				<h3 class="text-xl font-semibold mb-2 text-blue-300">Join a Guild</h3>
				<p class="text-gray-400">Connect with like-minded adventurers and tackle challenging quests together</p>
			</div>
			
			<div class="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-pink-500/30">
				<div class="text-3xl mb-4">💎</div>
				<h3 class="text-xl font-semibold mb-2 text-pink-300">Earn Epic Loot</h3>
				<p class="text-gray-400">Complete dungeons, gain experience, and collect legendary rewards</p>
			</div>
		</div>
		
		<div class="bg-gray-800/30 backdrop-blur-sm rounded-lg p-4 border border-gray-600 inline-block">
			<p class="text-sm text-gray-400">
				API Status: <span class="text-green-400 font-semibold">{apiStatus}</span>
			</p>
		</div>
	</div>
</div>