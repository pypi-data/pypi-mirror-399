# ...  (الكود السابق) ...

    def suggest_improvements(self, shape: Dict[str, Any],
                            target_metrics: Optional[Dict[str, float]] = None) -> List[str]:
        """
        Suggest improvements for shape.  © 2025 MERO
        """
        
        vertices = np.array(shape['vertices'])
        analysis = self.analyze_shape(vertices, shape.get('edges'))
        
        suggestions = []
        
        if analysis['symmetry_analysis']['overall_symmetry'] < 0.5:
            suggestions. append('💡 Consider making the shape more symmetric for aesthetic appeal')
        
        if analysis['stability_analysis']['stability_score'] < 0.5:
            suggestions.append('⚠️ The shape may be unstable. Try concentrating vertices more towards center')
        
        if analysis['geometric_properties']['radius_variance'] > 0.5:
            suggestions.append('📐 High radius variance detected. Shape could be more uniform')
        
        if analysis['topological_properties']['degree_variance'] > 2:
            suggestions.append('🔗 Irregular vertex connectivity.  Consider rewiring edges')
        
        if analysis['aesthetic_score'] > 0.85:
            suggestions.append('🌟 Excellent aesthetic properties!')
        
        geo = analysis['geometric_properties']
        aspect_ratios = [
            geo. get('radius_max', 1) / (geo.get('radius_min', 1) + 1e-10)
        ]
        
        if aspect_ratios[0] > 3:
            suggestions.append('📏 Shape is highly elongated. Consider adjusting proportions')
        
        return suggestions
    
    def extract_patterns(self, vertices: np.ndarray,
                        pattern_type: str = 'all') -> Dict[str, Any]:
        """Extract patterns from shape. © 2025 MERO"""
        
        patterns = {}
        
        if pattern_type in ['all', 'spatial']:
            from scipy.cluster.hierarchy import dendrogram, linkage
            
            Z = linkage(vertices, method='ward')
            patterns['clustering'] = {
                'linkage_matrix': Z. tolist(),
                'num_clusters': len(np.unique(Z[: , 2]))
            }
        
        if pattern_type in ['all', 'spectral']:
            distances = distance.squareform(distance.pdist(vertices))
            eigenvalues = np.linalg.eigvals(distances)
            patterns['spectral_signature'] = np.sort(eigenvalues)[::-1]. tolist()[:10]
        
        if pattern_type in ['all', 'frequency']:
            from scipy.fft import fft
            
            fft_result = fft(vertices. flatten())
            patterns['frequency_components'] = np.abs(fft_result)[: 20]. tolist()
        
        patterns['developer'] = 'MERO'
        patterns['version'] = '1.0.0'
        
        return patterns