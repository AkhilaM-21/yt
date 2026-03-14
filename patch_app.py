with open("frontend/src/App.js", "r") as f:
    content = f.read()

content = content.replace("import { youtubeAPI } from './services/api';", "import { youtubeAPI, instagramAPI } from './services/api';")

state_replace = """
  const [pageSize, setPageSize] = useState(10);
  const [platform, setPlatform] = useState('YouTube');
  const { toast } = useToast();
"""
content = content.replace("  const [pageSize, setPageSize] = useState(10);\n  const { toast } = useToast();", state_replace)

search_replace = """
    try {
      // Fetch only videos, calculate summary locally to avoid extra API calls and errors
      const videoResponse = platform === 'YouTube'
        ? await youtubeAPI.searchVideos(params)
        : await instagramAPI.searchPosts(params);

      const videos = videoResponse.videos || [];
"""
content = content.replace("""    try {
      // Fetch only videos, calculate summary locally to avoid extra API calls and errors
      const videoResponse = await youtubeAPI.searchVideos(params);

      const videos = videoResponse.videos || [];""", search_replace)

searchform_replace = """
        {/* Search Form */}
        <div className="mb-12">
          <SearchForm
            onSearch={handleSearch}
            loading={loading}
            platform={platform}
            setPlatform={setPlatform}
          />
        </div>
"""
content = content.replace("""        {/* Search Form */}
        <div className="mb-12">
          <SearchForm onSearch={handleSearch} loading={loading} />
        </div>""", searchform_replace)

with open("frontend/src/App.js", "w") as f:
    f.write(content)
